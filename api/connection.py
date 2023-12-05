import os
import configparser
import psycopg2 as db

SCHEMA_NAME = 'test_live_schema'

def connect_to_database(schema_name=SCHEMA_NAME):
    dirname = os.getcwd()
    config = configparser.ConfigParser()
    config.read(os.path.join(dirname, 'dbtool.ini'))
    conn = db.connect(dbname=os.getenv('DB_NAME'),
                      user=os.getenv('DB_USER'), 
                      password=os.getenv('DB_PASSWORD'),
                      host=os.getenv('DB_HOST'),
                      port=os.getenv('DB_PORT'),
                      client_encoding=os.getenv('DB_CLIENT_ENCODING'))
    curs = conn.cursor()
    return curs, config, conn