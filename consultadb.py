import json
import mysql.connector as sql_db 
import sys
import logging
import yaml
import json
import datetime

with open(r'conf/config.yaml') as file:
    yaml_config = yaml.load(file, Loader=yaml.FullLoader)



class mysql():
    def __init__(self):
        """ Constructor """
        logging.info("constructor")
        fecha = datetime.datetime.now()
        self.fecha_hoy = repr(fecha.strftime("%Y-%m-%d %H-%M-%S"))
        logging.warning("fecha hoy : " + self.fecha_hoy)
        
    def select_mysql(self, sql):
        print ("entro en select")
        mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = mysql_conexion.cursor()
        try:
            cursor.execute(sql)
            #records = cursor.fetchall()
            #print (records)
        except mysql.Error as error:
            print("Error: {}".format(error))
            logging.warning(error)
        try:
            row_headers=[x[0] for x in cursor.description]
            json_data=[]
            for result in cursor.fetchall():
                #print (result)
                json_data.append(dict(zip(row_headers,result)))
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            mysql_conexion.close()
        return json_data
        #return records

    def insert_mysql(self, sql):
        mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = mysql_conexion.cursor()
        try:
            logging.warning(sql)
            cursor.execute(sql)
            logging.warning("despues de execute")
            mysql_conexion.commit()

            print(cursor.rowcount, "record(s) affected")
            print(cursor.lastrowid)
            #id_jmeter = cursor.lastrowid
            #logging.info(cursor.fetchall())
        except mysql.Error as error:
            print("Error: {}".format(error))
            raise ValueError("Error: {}".format(error))
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            mysql_conexion.close()
        #return json.loads('{"sucess": "0"}')
        return 

    def update_mysql(self, sql):
        mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = mysql_conexion.cursor()
        logging.warning("update sql amigo")
        logging.warning(sql)
        try:
            cursor.execute(sql)
            mysql_conexion.commit()
            print(cursor.rowcount, "record(s) affected") 
            if cursor.rowcount == 0:
                logging.info("entro en el if")
                raise Exception("Error : no se modifico ninguna columna") 
            else:
                logging.info("entro en el else")
                logging.info(cursor.rowcount)
        except mysql.Error as error:
            print("Error: {}".format(error))
            raise ValueError("Error: {}".format(error))
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            mysql_conexion.close()
        return json.loads('{"sucess": "0"}')
