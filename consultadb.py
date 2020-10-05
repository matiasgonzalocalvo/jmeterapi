import json
#import mysql.connector 
#as mysql
#import mysql
#import mariadb
import mysql.connector as sql_db 
import sys
import logging
import yaml
import json

with open(r'conf/config.yaml') as file:
    yaml_config = yaml.load(file, Loader=yaml.FullLoader)



class mysql():
    def select_mariadb(self, sql):
        mariadb_conexion = mariadb.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = mariadb_conexion.cursor()
        try:
            cursor.execute(sql)
        except mariadb.Error as error:
            print("Error: {}".format(error))
            logging.warning(error)
        try:
            row_headers=[x[0] for x in cursor.description]
            json_data=[]
            for result in cursor.fetchall():
                json_data.append(dict(zip(row_headers,result)))
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            mariadb_conexion.close()
        return json_data

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

    def update_mariadb(self, sql):
        mariadb_conexion = mariadb.connect(host=yaml_config['db']['host'], port=yaml_config['db']['port'],user=yaml_config['db']['user'], password=yaml_config['db']['password'], database=yaml_config['db']['database'])
        cursor = mariadb_conexion.cursor()
        logging.warning(sql)
        try:
            cursor.execute(sql)
            mariadb_conexion.commit()
            print(cursor.rowcount, "record(s) affected") 
            if cursor.rowcount == 0:
                logging.info("entro en el if")
                raise Exception("Error : no se modifico ninguna columna") 
            else:
                logging.info("entro en el else")
                logging.info(cursor.rowcount)
        except mariadb.Error as error:
            print("Error: {}".format(error))
            raise ValueError("Error: {}".format(error))
        except Exception as e:
            raise ValueError("Error: {}".format(e))
        finally:
            mariadb_conexion.close()
        return json.loads('{"sucess": "0"}')
