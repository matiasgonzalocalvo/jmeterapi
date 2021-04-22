import logging
from consultadb import *
import json
#import datetime
import urllib.parse
from datetime import datetime

with open(r'conf/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class class_jmeter():
    """ Clase """
    def __init__(self):
        """ Constructor """
        logging.info("constructor")
        fecha = datetime.now()
        self.fecha_hoy = repr(fecha.strftime("%Y-%m-%d"))
        logging.info("fecha hoy : " + self.fecha_hoy)
        
    
    def add_test(self, nombre_del_proyecto, path_files, file_jmx, CMDB , USER, USER_TOKEN , file_properties="NULL", file_files="NULL", mensaje="NULL", DATE="NULL", NOW="False", DURATION="NULL", estate="NULL", influx_appname="NULL"):

        """ Agregar un nuevo articulo """
        saved_args = locals()
        print("saved_args is", saved_args)
        #Begin Negrada 
        nombre_del_proyecto = repr(nombre_del_proyecto)
        path_files = repr(path_files)
        file_jmx = repr(file_jmx)
        
        if file_properties is None:
            file_properties = "NULL"
        else:
            file_properties = repr(file_properties)
        
        if influx_appname is None:
            influx_appname = "NULL"
        else:
            influx_appname = repr(influx_appname)
            
        if file_files is None:
            file_files = "NULL"
        else:
            file_files = repr(file_files)
        
        if  DATE is None:
            DATE = "NULL"
            print (DATE)
        else:
            DATE =  f"'{DATE.strftime('%Y-%m-%d %H:%M:%S')}'"
        
        if mensaje is None:
            mensaje = "NULL"
        else:
            mensaje = repr(mensaje)
            
        if NOW is None:
            NOW = False
        
        if DURATION is None:
            DURATION = "NULL"
        
        if estate is not None:
            estate = repr(estate)
        #Finish Negrada
        CMDB = repr(CMDB)
        USER = repr(USER)
        
        USER_TOKEN =  repr(USER_TOKEN)
        sql = f"""INSERT INTO jmeter (CMDB, "USER" , USER_TOKEN , app_name, files_path, jmx, properties, otherfiles, message, start_datetime, now, createdate, duration, estate, influx_appname) 
        VALUES({CMDB}, {USER} , {USER_TOKEN} , {nombre_del_proyecto}, {path_files}, {file_jmx}, {file_properties}, {file_files}, {mensaje}, {DATE}, {NOW}, {self.fecha_hoy}, {DURATION}, {estate}, {influx_appname});"""
        logging.warning("sql")
        logging.warning(sql)
        try:
            jmeter_db = postgresql()
            jmeter_db.insert_postgresql(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))
        
    def get_test(self, search):
        logging.warning("get_test")
        """ Lista los jobs """
        sql = """SELECT CMDB, app_name, influx_appname, 
            \"USER\", USER_TOKEN,  files_path, jmx, 
            properties, otherfiles, message, 
            coalesce(to_char(init_datetime , 'DD/MM/YYYY HH24:SS'),'-') AS init_datetime ,
            coalesce(to_char(createdate , 'DD/MM/YYYY'),'-') AS createdate , 
            hostname, estate, duration, 
            coalesce(to_char(start_datetime , 'DD/MM/YYYY HH24:SS'),'-') AS start_datetime 
            FROM jmeter 
            WHERE app_name ILIKE '%""" + search + """%' 
            OR influx_appname ILIKE '%""" + search + """%' 
            OR CMDB ILIKE '%""" + search + """%' 
            OR USER_TOKEN ILIKE '%""" + search + """%' 
            OR 'USER' ILIKE '%""" + search + """%' 
            OR estate ILIKE '%""" + search + """%' 
            ORDER BY createdate DESC"""
        logging.warning(sql)
        articulos_get = postgresql()
        #yaml_sql = yaml_config['sql']['sql_get_sucursales']
        salida = articulos_get.select_postgresql(sql)
        #return articulos_get.select_mariadb(sql)
        logging.info("muestro salida")
        logging.info(salida)
        url = config['grafana']['url']
        for index in range(len(salida)):
            if salida[index]["init_datetime"] == "-":
                logging.info("Todavia no se ejecuto no tiene init date no puedo armar la url de grafana , muestro init_date")
                logging.info(salida[index]["init_datetime"])
            else:    
                dt = datetime.strptime(salida[index]["init_datetime"], '%d/%m/%Y %H:%M')
                #Fix 60 minutos y 60 minutos despues del init_datetime revisar por que no coincide con el del influxdb
                FROM = int((dt - datetime(1970, 1, 1)).total_seconds() * 1000 - 60 * 60000)
                TO = int((dt - datetime(1970, 1, 1)).total_seconds() * 1000 + 60 * 60000)
                getVars = {"var-data_source": "InfluxDB-Jmeter", "var-application": salida[index]["influx_appname"], "var-measurement_name": "jmeter", "from": FROM, "to": TO}
                grafana_url = url + urllib.parse.urlencode(getVars)
                salida[index]["grafana_url"] = grafana_url
        return salida