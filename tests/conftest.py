# conftest.py for setting up mock database #
import os
import pytest
import configparser
import psycopg2 as db

SCHEMA_NAME = 'test_schema'

@pytest.fixture
def connect_to_database(schema_name=SCHEMA_NAME):
    dirname = os.getcwd()
    config = configparser.ConfigParser()
    config.read(os.path.join(dirname, 'api/dbtool.ini'))
    conn = db.connect(dbname=os.getenv("DB_NAME"),
                      user=os.getenv("DB_USER"), 
                      password=os.getenv("DB_PASSWORD"),
                      host=os.getenv("DB_HOST"),
                      port=os.getenv("DB_PORT")
                      )
    curs = conn.cursor()
    curs.execute(config['create_schema']['new_schema'].replace('@schema_name@', schema_name))
    return curs, config

@pytest.fixture
def create_charity_table(connect_to_database, schema_name=SCHEMA_NAME):
    (curs, config) = connect_to_database
    # Create the charity table in the test schema, should be empty
    curs.execute(config['create_table']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME
    ))
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'charity'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 0)

@pytest.fixture
def create_schedule_table(connect_to_database, create_charity_table, schema_name=SCHEMA_NAME): 
    (curs, config) = connect_to_database
    # Create the schedule table in the test schema, should be empty
    curs.execute(config['create_table']['day_enum'].replace(
        '@schema_name@', SCHEMA_NAME
    ))
    curs.execute(config['create_table']['time_enum'].replace(
        '@schema_name@', SCHEMA_NAME
    ))
    curs.execute(config['create_table']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME
    ))
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 0)
    

@pytest.fixture
def create_message_table(connect_to_database, create_charity_table, schema_name=SCHEMA_NAME): 
    (curs, config) = connect_to_database
    # Create the message table in the test schema, should be empty
    curs.execute(config['create_table']['message_table'].replace(
        '@schema_name@', SCHEMA_NAME
    ))
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'message'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 0)