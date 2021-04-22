#Matias Gonzalo Calvo | matiasgonzalocalvo@gmail.com | matcalvo@santandertecnologia.com.ar

from flask import Flask, request, jsonify, json, Response, stream_with_context, g, url_for
from flask_restplus import Api, Resource, fields, cors, reqparse, inputs
import yaml
import logging
import requests
import uuid
import os 
from flask_cors import CORS, cross_origin
#jwt keycloack
from flask_oidc import OpenIDConnect
#para subir los archivos
from werkzeug.datastructures import FileStorage
from jmeter import *
#para buscar
import re 
import subprocess

#debug 
logging.basicConfig(level=logging.DEBUG)

flask_app = Flask(__name__)

#Fix Cors Como odio los cors
CORS(flask_app, supports_credentials=True, resources={r"*": {"origins": "*"}})

#Fix https
@property
def specs_url(self):
    return url_for(self.endpoint('specs'), _external=True, _scheme='https')    
Api.specs_url = specs_url

#creo la api
app = Api(app = flask_app, version = "0.1", title = "Jmeter Api", description = "Apis desarrolladas por el equipo SRE Banco Santander Argentina")

#Configuracion de keycloak 
flask_app.config.update({
    'SECRET_KEY': 'SomethingNotEntirelySecret',
    'TESTING': True,
    'DEBUG': True,
    'OIDC_CLIENT_SECRETS': 'conf/client_secrets.json',
    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
    'OIDC_USER_INFO_ENABLED': True,
    'OIDC_OPENID_REALM': 'jmeter',
    'OIDC_SCOPES': ['openid', 'email', 'profile'],
    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
})
oidc = OpenIDConnect(flask_app)

#creo los 2 namespace
jmeter = app.namespace('createtest', description='upload file')
get_jmeter = app.namespace('gettest', description='get all jobs')

#Leo el archivo de configuracion 
with open(r'conf/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)


jmeter_model = app.model('Modelo Jmeter',
                                {
                                    'nombre_del_proyecto': fields.String(required = True, description="Nombre de la prueba", help="Pone el nombre gato que onda"),
                                })

upload_parser = jmeter.parser()
upload_parser.add_argument('nombre_del_proyecto', type=str, help='nombre del proyecto' ,required=True)
upload_parser.add_argument('jmx', location='files',type=FileStorage, required=True)
upload_parser.add_argument('Authorization', type=str, location='headers', help='Bearer Access Token' ,required=True)
upload_parser.add_argument('CMDB', type=str, help='CMDB' ,required=True)
upload_parser.add_argument('USER', type=str, help='User' ,required=True)
upload_parser.add_argument('now', type=inputs.boolean,  help='ahora si o no ' ,required=True)
upload_parser.add_argument('properties', location='files',type=FileStorage,  required=False)
upload_parser.add_argument('files', location='files',type=FileStorage, required=False)
upload_parser.add_argument('date', type=inputs.datetime_from_iso8601, help='2012-01-01T23:30:00+02:00' ,required=False)
upload_parser.add_argument('time', type=inputs.datetime,  help='2012-01-01T23:30:00+02:00' ,required=False)
upload_parser.add_argument('duration', type=int,  help='1-60' ,required=False)
upload_parser.add_argument('message', type=str,  help='mensaje amigo ' ,required=False)

@jmeter.route("/")
@jmeter.expect(upload_parser, validate=True)
class MainClass(Resource):
    @oidc.accept_token(require_token=True)
    def post(self):
        #Genero un uuid aleatorio 
        idjmeter = str(uuid.uuid4())
        args = upload_parser.parse_args()
        logging.info(args)
        path = config['path']['files'] + idjmeter + "-" + args['nombre_del_proyecto'] + "/"
        try:
            if args['now'] is None:
                if args['date'] is None:
                    print ("aguante el rojo")
                    raise ValueError("Error: no se si ejecutarlo ")
        except Exception as e:
            logging.info("error la variable now y el date no estan definidos no se pasaron por parametros me estas llamando de cualquier manera amigo")
            jmeter.abort(500, status = "error la variable now y el date no estan definidos no se pasaron por parametros me estas llamando de cualquier manera amigo" + str(e), statusCode = "500")
        try:
            os.mkdir(path)
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "No pude crear el directorio Consultar con el admin" + path + str(e), statusCode = "500")
        try:
            for i in "jmx", "properties", "files":
                logging.info("el for va por el archivo " + i)
                logging.info(args[i])
                if args[i] is not None:
                    logging.info("Guardo el archivo : " + args[i].filename + "en el path : " + path)
                    args[i].save( path + args[i].filename)
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "No pude subir el archivo: " + args[i].filename + "en el path  " + path + str(e), statusCode = "500")
        logging.info(args['properties'])
        logging.info("path")
        logging.info(path)
        if args['properties'] is None:
            file_properties = None
        else:
            file_properties = repr(args['properties'].filename)
        if args['files'] is None:
            file_files = None
        else:
            file_files = repr(args['files'].filename)
        logging.info("antes de jmeter_create_test")
        USER_TOKEN = g.oidc_token_info['preferred_username']
        filejmx = path + args["jmx"].filename
        try:
            with open(filejmx) as myfile:
                if not 'BackendListener' in myfile.read():
                    logging.info("CRITICAL : no encontre la palabra BackendListener")
                    raise ValueError("Error: el jmx no tiene el BackendListener")
        except Exception as e:
            jmeter.abort(400, e.__doc__, status = "Fallo amigo el jmx no tiene el backenlistener" +  str(e), statusCode = "400")
            
        try:
            
            extract_command = f""" cat "{filejmx}" |grep -i 'name="application"' -A 2|grep application -A 1  |grep "Argument.value" |awk -F">" '{{print $2}}'|awk -F"<" '{{print $1}}'|awk -F"," '{{ if ( $0 ~ "__P") {{print $2}} else {{print $0}} }}'|sed 's/)}}//g' """
            process = subprocess.Popen(extract_command, stdout=subprocess.PIPE,stderr=subprocess.PIPE,stdin=subprocess.PIPE, shell=True)
            influx_appname = process.communicate()[0].strip()
            logging.info(influx_appname)
            logging.info(process.returncode)
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "Fallo amigo no pude obtener el nombre de appname de influx adentro del jmx" +  str(e), statusCode = "500")
        try:
            jmeter_create_test = class_jmeter()
            jmeter_create_test.add_test(args['nombre_del_proyecto'], path, args['jmx'].filename,  args['CMDB'], args['USER'], USER_TOKEN, file_properties, file_files, args['message'], args['date'], args['now'], args['duration'], "pendiente",influx_appname.decode('utf-8'))
            logging.info("return 200")
            return '200'
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "Fallo amigo consultar con el admin" +  str(e), statusCode = "500")


@get_jmeter.route("/<string:nombre>")
class MainClass(Resource):
    @oidc.accept_token(require_token=True)
    @jmeter.doc(params={'nombre': 'nombre del jmenter job', 'Authorization': {'in': 'header', 'description': 'An authorization token example : Bearer JWT_TOKEN'}},responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
    def get(self,nombre):
        try:
            logging.info(g.oidc_token_info['sub'])
            logging.info(g.oidc_token_info['preferred_username'])
            logging.info(g.oidc_token_info['email'])
        except Exception as e:
            logging.info("seguro no tiene email")
            logging.info(e)
        try:
            logging.info("nombre : ")
            logging.info(nombre)
            jmeter_get_test = class_jmeter()
            get = jmeter_get_test.get_test(nombre)
            logging.info(get)
            return get
        except KeyError as e:
            jmeter.abort(500, e.__doc__, status = "Could not save information" + str(e), statusCode = "500")
        except Exception as e:
            jmeter.abort(400, e.__doc__, status = "Could not save information" + str(e), statusCode = "400")
        else:
            x =  '{ "status": "ok", "statusCode":200, "message":"por ahora no hace una verga"}'
            logging.warning(json.dumps(x))
            return json.loads(x)
     

if __name__ == '__main__':
    print(config['host']['host'],config['host']['port'])
    flask_app.run(debug=True,host=config['host']['host'],port=config['host']['port'])