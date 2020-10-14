#Matias Gonzalo Calvo | matiasgonzalocalvo@gmail.com | matcalvo@santandertecnologia.com.ar

from flask import Flask, request, jsonify, json, Response, stream_with_context, g
from flask_restplus import Api, Resource, fields, cors, reqparse, inputs
import yaml
import logging
import requests
import uuid
import os 

from flask_cors import CORS, cross_origin

#jwt keycloack
#from flask_oidc import OpenIDConnect


#para subir los archivos
from werkzeug.datastructures import FileStorage

from createtest import *

#debug 
logging.basicConfig(level=logging.DEBUG)

flask_app = Flask(__name__)
#CORS(flask_app)
#Fix Cors Como odio los cors
CORS(flask_app, supports_credentials=True, resources={r"*": {"origins": "*"}})

#Fix keycloack redirect
#flask_app.config['OVERWRITE_REDIRECT_URI'] = 'https://farmasaludapi.mgcalvo.com/oidc_callback'

#Fix https
#@property
#def specs_url(self):
#    return url_for(self.endpoint('specs'), _external=True, _scheme='https')    
#Api.specs_url = specs_url

app = Api(app = flask_app, version = "0.1", title = "Jmeter Api", description = "Apis desarrolladas por el equipo SRE Banco Santander Argentina")

#flask_app.config.update({
#    'SECRET_KEY': 'SomethingNotEntirelySecret',
#    'TESTING': True,
#    'DEBUG': True,
#    'OIDC_CLIENT_SECRETS': 'conf/client_secrets.json',
#    'OIDC_ID_TOKEN_COOKIE_SECURE': False,
#    'OIDC_REQUIRE_VERIFIED_EMAIL': False,
#    'OIDC_USER_INFO_ENABLED': True,
#    'OIDC_OPENID_REALM': 'farmasalud',
#    'OIDC_SCOPES': ['openid', 'email', 'profile'],
#    'OIDC_INTROSPECTION_AUTH_METHOD': 'client_secret_post'
#})

#oidc = OpenIDConnect(flask_app)
#sucursales = app.namespace('sucursales', description='Manejar Sucursales')
#articulos = app.namespace('articulos', description='Manejar articulos')
#inventory = app.namespace('inventory', description='Manejar articulos')
#user = app.namespace('user', description='Manejar articulos')
#login = app.namespace('login', description='login')
#logout = app.namespace('logout', description='login')
jmeter = app.namespace('createtest', description='upload file')

with open(r'conf/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

#agregararticulo_model = app.model('Modelo agregar articulo',
#                                {
#                                    'nombre_del_articulo': fields.String(required = True, description="nombre del articulo", help="no puede estar en blanco",max_length=50), 
#                                    'marca_del_articulo': fields.String(required = True, description="marca del articulo", help="no puede estar en blanco",max_length=50),
#                                    'precio': fields.Float(required = True, description="Precio del articulo", help="no puede estar en blanco"),
#                                    'barcode': fields.String(required = True, description="Barcode del articulo", help="no puede estar en blanco",max_length=16,min_length=16),
#                                    'descripcion': fields.String(required = True, description="Descripcion del articulo", help="no puede estar en blanco",max_length=100),
#                                })

#prueba_model = app.model('Modelo Search articulo',
#                                {
#                                    'all': fields.Boolean(required = False, description="marca del articulo", help="no puede estar en blanco",max_length=50),
#                                })

#updateinventario_model = app.model('Modelo agregar y eliminar inventario',
#                                {
#                                    'sucursal_id': fields.Integer(required = True, description="Sucursal", help="no puede estar en blanco",max_length=50), 
#                                    'cantidad': fields.Integer(required = True, description="Cantidad de articulos", help="no puede estar en blanco",max_length=50),
#                                    'fecha_vencimiento': fields.DateTime(required = True, description="fecha de vencimiento del articulo", help="no puede estar en blanco"),
#                                    'barcode': fields.String(required = True, description="Barcode del articulo", help="no puede estar en blanco",max_length=16,min_length=16),
#                                })

jmeter_model = app.model('Modelo Jmeter',
                                {
                                    'nombre_del_proyecto': fields.String(required = True, description="Nombre de la prueba", help="Pone el nombre gato que onda"),
                                    'estado': fields.String(required = True, description="Estado del job", help="El estado del job puede ser 'pendiente','cancelado','procesando','error','ok','procesado','tomado'"),
                                })

#tax_type = app.model("tax", {"tax_form": fields.String()})

#jmeter_model = app.model("modelo",{})
upload_parser = jmeter.parser()
upload_parser.add_argument('jmx', location='files',type=FileStorage, required=True)
upload_parser.add_argument('properties', location='files',type=FileStorage,  required=False)
upload_parser.add_argument('files', location='files',type=FileStorage, required=False)
upload_parser.add_argument('date', type=inputs.datetime_from_iso8601, help='2012-01-01T23:30:00+02:00' ,required=False)
upload_parser.add_argument('time', type=inputs.datetime,  help='2012-01-01T23:30:00+02:00' ,required=False)
upload_parser.add_argument('duration', type=int,  help='1-5' ,required=False)
upload_parser.add_argument('nombre_del_proyecto', type=str, help='nombre del proyecto' ,required=True)
upload_parser.add_argument('now', type=inputs.boolean,  help='ahora si o no ' ,required=False)
upload_parser.add_argument('message', type=str,  help='mensaje amigo ' ,required=False)


#parser = reqparse.RequestParser()
#parser.add_argument('tax_form', required = True)

@jmeter.route("/")
#@jmeter.expect(parser,upload_parser, validate=True)
@jmeter.expect(upload_parser, validate=True)
class MainClass(Resource):
    #@jmeter.doc(responses={ 200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
    #@jmeter.expect(jmeter_model, validate=True)
    #@jmeter.expect(tax_type, upload_parser, validate=True)
    #@jmeter.expect(parser)
    
    def post(self):
        idjmeter = str(uuid.uuid4())
        #logging.info(idjmeter)
        args = upload_parser.parse_args()
        logging.info(args)
        path = config['path']['files'] + idjmeter + "-" + args['nombre_del_proyecto'] + "/"
        try:
            if args['now'] is None:
                if args['date'] is None:
                    print ("aguante el rojo")
                    raise ValueError("Error: no se si ejecutarlo ")
        except TypeError:
            logging.info("error la variable now y el date no estan definidos no se pasaron por parametros me esas llamando de cualquier manera amigo")
            #logging.info(args['now'])
            #logging.info(args['date'])
        
        try:
            os.mkdir(path)
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "No pude creapostr el directorio " + path + str(e), statusCode = "500")
            
        try:
            for i in "jmx", "properties", "files":
                logging.info("el for va por el archivo " + i)
                logging.info(args[i])
                if args[i] is not None:
                    logging.info("Guardo el archivo : " + args[i].filename + "en el path : " + path)
                    args[i].save( path + args[i].filename)
                #args['properties'].save( path + args['properties'].filename)
        except Exception as e:
            jmeter.abort(500, e.__doc__, status = "No pude subir el archivo: " + args[i].filename + "en el path  " + path + str(e), statusCode = "500")
                    
        jmeter_create_test = createtest()
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
        jmeter_create_test.add_test(args['nombre_del_proyecto'], path, args['jmx'].filename, file_properties, file_files, args['message'], args['date'], args['now'], args['duration'], "pendiente")
        return '200'

@jmeter.route("/<string:nombre>/<string:estado>")
class MainClass(Resource):
    #@oidc.require_login
    @jmeter.doc(params={'nombre': 'nombre del jmenter job', "estado" : "pendiente all etc"},responses={200: 'OK', 400: 'Invalid Argument', 500: 'Mapping Key Error' })
    def get(self,nombre,estado):
        try:
            print ("probeshion")
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
