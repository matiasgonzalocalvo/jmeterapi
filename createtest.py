import logging
from consultadb import *
import json
import datetime

with open(r'conf/config.yaml') as file:
    config = yaml.load(file, Loader=yaml.FullLoader)

class createtest():
    """ Clase """
    def __init__(self):
        """ Constructor """
        logging.info("constructor")
        fecha = datetime.datetime.now()
        self.fecha_hoy = repr(fecha.strftime("%Y-%m-%d"))
        logging.info("fecha hoy : " + self.fecha_hoy)
        
    
    def add_test(self, nombre_del_proyecto, path_files, file_jmx, file_properties="NULL", file_files="NULL", mensaje="NULL", DATE="NULL", NOW="False", DURATION="NULL", estate="NULL"):

        """ Agregar un nuevo articulo """
        saved_args = locals()
        print("saved_args is", saved_args)
        
        nombre_del_proyecto = repr(nombre_del_proyecto)
        path_files = repr(path_files)
        file_jmx = repr(file_jmx)
        
        if file_properties is None:
            file_properties = "NULL"
        else:
            file_properties = repr(file_properties)
            
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
        
            
        sql = f"""INSERT INTO jmeter.jmeter (app_name, files_path, jmx, properties, otherfiles, message, start_datetime, now, createdate, duration, estate) 
        VALUES({nombre_del_proyecto}, {path_files}, {file_jmx}, {file_properties}, {file_files}, {mensaje}, {DATE}, {NOW}, {self.fecha_hoy}, {DURATION}, {estate});"""
        logging.warning("sql")
        logging.warning(sql)
        try:
            jmeter_db = mysql()
            jmeter_db.insert_mysql(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))