import psycopg as mock_db
import os
import configparser

dirname = os.getcwd()
config = configparser.ConfigParser()
config.read(os.path.join(dirname, 'tests/assets/mock_dbtool.ini'))
print(config.sections())

conn = mock_db.connect(**config['connection'])
curs = conn.cursor()

#curs.execute(config['delete_test_schema']['delete_test_database'])
curs.execute(config['create_test_schema']['test_database'])
#curs.execute(config['delete_charity_table']['delete_charities'])
curs.execute(config['create_charity_table']['charity_table'])
curs.execute(config['insert_into_charity_table']['insert_svp'])
curs.execute(config['sample_charity_query']['all_charities'])
rec=curs.fetchall()
print(rec)

#conn.commit() - will use only for the live database
conn.close()