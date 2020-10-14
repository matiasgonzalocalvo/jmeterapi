import json
import mysql.connector as sql_db 
from consultadb import *
import sys
import logging
import yaml
import json
import socket
import time
import subprocess
with open(r'conf/config.yaml') as file:
    yaml_config = yaml.load(file, Loader=yaml.FullLoader)
    

class jmeter():
    def jmeter_exec(self, path_files, file_jmx, file_properties="NULL", file_files="NULL", duration="NULL"):
        saved_args = locals()
        logging.warning("saved_args is", saved_args)
        logging.warning(path_files)
        logging.warning(file_jmx)
        logging.warning(file_properties)
        logging.warning(file_files)
        jmeter_command = f"""
        #echo {path_files};
        cd {path_files} ;
        #pwd ;
        ARGS="-n -t {path_files}/{file_jmx} -Dserver.rmi.ssl.disable=true" ; 
        if ! [ -z {file_properties} -o "{file_properties}" = "NULL" -o "{file_properties}" = "None" ] ; then
            echo "file properties es  == {file_properties} "
            ARGS="$ARGS -G{file_properties}" ; 
        fi
        if ! [ -z {duration} -o {duration} = "NULL" -o {duration} = "None" ] ; then
            echo "duration es  == {duration} "
            duration={duration}m
        else
            duration="1m"
        fi
        echo "timeout $duration /jmeter/apache-jmeter-5.3/bin/jmeter $ARGS -l {path_files}/prueba-jmeter.log"
        timeout $duration /jmeter/apache-jmeter-5.3/bin/jmeter $ARGS -l {path_files}/prueba-jmeter.log
        """
        process = subprocess.Popen(jmeter_command, stdout=subprocess.PIPE, shell=True)
        #output, error = process.communicate()
        #logging.warning("salida de la ejecucion")
        #logging.warning(output)
        #logging.warning(error)
        proc_stdout = process.communicate()[0].strip()
        logging.warning(proc_stdout)
        logging.warning(process.returncode)
        if ( process.returncode == 0 ):
            logging.warning("proceso termino correctamente")
        elif (process.returncode == 124 ): 
            logging.warning("el proceso acabo por el timeout revisar salida")
        else:
            logging.warning(f"salida que no manejo {process.returncode}")
            raise ValueError(f"Error: {process.returncode}")
        
        
        
if __name__ == '__main__':
    fecha = datetime.datetime.now()
    fecha_hoy = repr(fecha.strftime("%Y-%m-%d %H-%M-%S"))
    logging.warning("fecha hoy : " + fecha_hoy)
    jmeterdb = mysql()
    sql_pendiente = """ 
        SELECT estate, id, app_name, files_path, jmx, properties, otherfiles, now, hostname, duration
        FROM jmeter.jmeter
        WHERE estate = 'pendiente'
    """
    sql_tomado = """ 
        SELECT estate, id, app_name, files_path, jmx, properties, otherfiles, now, hostname, duration
        FROM jmeter.jmeter
        WHERE estate = 'tomado'
    """
    logging.warning(sql_pendiente)
    #json.loads('{"sucess": "0"}')}
    jmeterselect = jmeterdb.select_mysql(sql_pendiente)
    #print (json)

             
    for result in jmeterselect:
        logging.warning(result)
        logging.warning(result['estate'])
        if (result['estate'] == 'pendiente'):
            logging.warning("aca ejecuto el jmeter y dsp insert y toda la bola")
        if result['hostname'] is None or result['hostname'] == '' :
            logging.warning("hostname is none set hostname")
            logging.warning(socket.gethostname())
            sql_set_hostname = f"""
                UPDATE jmeter.jmeter
                SET hostname="{socket.gethostname()}", estate="tomado", init_datetime={fecha_hoy}
                WHERE id={result['id']};
            """
            jmeterdb.update_mysql(sql_set_hostname)
            break
    #time.sleep(2)
    
    jmeterselect_tomado = jmeterdb.select_mysql(sql_tomado)
    for result in jmeterselect_tomado:
        if ( result['hostname'] == socket.gethostname() ):
            logging.warning(result)
            logging.warning("el hostname es el mismo amigo bien ahi")
            j = jmeter()
            try:
                j.jmeter_exec(result['files_path'] ,result['jmx'] ,result['properties'] , result['otherfiles'])       
            except Exception as e:
                logging.warning("Error salida: {}".format(e))
                #raise ValueError("Error: {}".format(e))
                logging.warning("fallo amigo")