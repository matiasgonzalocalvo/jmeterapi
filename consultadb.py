import json
#import mysql.connector as sql_db 
import psycopg2
#import sys
import logging
import yaml
import json
import datetime

with open(r'conf/config.yaml') as file:
    yaml_config = yaml.load(file, Loader=yaml.FullLoader)



class postgresql():
    def __init__(self):
        """ Constructor """
        logging.info("constructor")
        fecha = datetime.datetime.now()
        self.fecha_hoy = repr(fecha.strftime("%Y-%m-%d %H-%M-%S"))
        logging.warning("fecha hoy : " + self.fecha_hoy)
        
    def select_postgresql(self, sql):
        print ("entro en select")
        conn = psycopg2.connect(host=yaml_config['db']['host'],database=yaml_config['db']['database'],user=yaml_config['db']['user'],password=yaml_config['db']['password'])
        #mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = conn.cursor()
        try:
            cursor.execute(sql)
            #records = cursor.fetchall()
            #print (records)
        except Exception as error:
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
            conn.close()
        return json_data
        #return records

    def insert_postgresql(self, sql):
        conn = psycopg2.connect(host=yaml_config['db']['host'],database=yaml_config['db']['database'],user=yaml_config['db']['user'],password=yaml_config['db']['password'])
        #mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = conn.cursor()
        try:
            logging.warning(sql)
            cursor.execute(sql)
            logging.warning("despues de execute")
            conn.commit()

            print(cursor.rowcount, "record(s) affected")
            print(cursor.lastrowid)
            #id_jmeter = cursor.lastrowid
            #logging.info(cursor.fetchall())
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            conn.close()
        #return json.loads('{"sucess": "0"}')
        return 

    def update_postgresql(self, sql):
        conn = psycopg2.connect(host=yaml_config['db']['host'],database=yaml_config['db']['database'],user=yaml_config['db']['user'],password=yaml_config['db']['password'])
        #mysql_conexion = sql_db.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = conn.cursor()
        logging.warning("update sql amigo")
        logging.warning(sql)
        try:
            cursor.execute(sql)
            conn.commit()
            print(cursor.rowcount, "record(s) affected") 
            if cursor.rowcount == 0:
                logging.info("entro en el if")
                raise Exception("Error : no se modifico ninguna columna") 
            else:
                logging.info("entro en el else")
                logging.info(cursor.rowcount)
        except Exception as e:
            print("Error: {}".format(e))
            raise ValueError("Error: {}".format(e))
        finally:
            conn.close()
        return json.loads('{"sucess": "0"}')
