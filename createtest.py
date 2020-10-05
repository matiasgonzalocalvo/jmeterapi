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

    def get_articulos(self, search):
        """ Lista los articulos que coincidan con search """
        logging.warning("get_articulos")
        sql = "SELECT articulo.idproduct, articulo.barcode, articulo.nombre, articulo.precio, articulo.descripcion, articulo.marca FROM efip.articulo WHERE articulo.nombre LIKE '%" + search + "%'" 
        logging.warning(sql)
        articulos_get = mariadb_efip()
        #yaml_sql = yaml_config['sql']['sql_get_sucursales']
        salida = articulos_get.select_mariadb(sql)
        #return articulos_get.select_mariadb(sql)
        return salida
    
    def add_inventario(self,sucursal,cantidad,fecha_vencimiento,barcode):
        """ Agregar un nuevo inventario a articulo """
        sql = "call add_inventario('" + str(fecha_vencimiento) + "','" + str(barcode) + "','" + str(sucursal) + "','" + str(cantidad) + "')"
        logging.info(sql)
        try:
            add_inventario = mariadb_efip()
            add_inventario.insert_mariadb(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))

    def del_inventario(self,sucursal,cantidad,fecha_vencimiento,barcode):
        """ Agregar un nuevo inventario a articulo """
        #sql = "call add_inventario('" + str(fecha_vencimiento) + "','" + str(self.fecha_hoy) + "','" + str(barcode) + "','" + str(sucursal) + "','" + str(cantidad) + "')"
        sql = "UPDATE inventario SET cantidad=cantidad-" + str(cantidad) + " WHERE barcode='" + str(barcode) + "' AND fecha_venc='" + str(fecha_vencimiento) + "' AND sucursales_id = " + str(sucursal) + " "
        logging.info(sql)
        try:
            add_inventario = mariadb_efip()
            add_inventario.update_mariadb(sql)
            return 
        except Exception as e:
            print("Error salida: {}".format(e))
            raise ValueError("Error: {}".format(e))
        
    def get_inventory(self, search):
        logging.warning("get_inventory")
        """ Lista los articulos que coincidan con search """
        sql = "SELECT articulo.idproduct, articulo.barcode, articulo.nombre, articulo.precio, articulo.descripcion, articulo.marca, IFNULL(DATE_FORMAT(inventario.fecha_venc , '%d/%m/%Y'),'-') AS fecha_venc , IFNULL(inventario.sucursales_id,'-') as sucursales_id, IFNULL(FORMAT(SUM(inventario.cantidad),0),'-') cantidad , IFNULL(sucursales.nombre,'-') as sucursal_nombre FROM efip.articulo LEFT JOIN efip.inventario ON inventario.barcode  = articulo.barcode LEFT JOIN efip.sucursales ON inventario.sucursales_id = sucursales.id WHERE  articulo.barcode  LIKE '%" + search + "%' OR articulo.nombre LIKE '%" + search + "%' GROUP BY IFNULL(fecha_venc,'-'),IFNULL(sucursales_id,'-'),nombre ORDER BY STR_TO_DATE(sucursales_id,'%d-%m-%Y') DESC"
        logging.warning(sql)
        articulos_get = mariadb_efip()
        #yaml_sql = yaml_config['sql']['sql_get_sucursales']
        salida = articulos_get.select_mariadb(sql)
        #return articulos_get.select_mariadb(sql)
        logging.info("muestro salida")
        logging.info(salida)
        return salida