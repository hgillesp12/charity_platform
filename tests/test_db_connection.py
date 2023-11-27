import psycopg as mock_db
import os
import configparser

dirname = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'tests/assets/mock_dbtool.ini'))

conn = mock_db.connect(**config['connection'])
curs = conn.cursor()

curs.execute(config['sample_query'])

conn.close()