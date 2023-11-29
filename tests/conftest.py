# conftest.py for setting up mock database #
import os
import pytest
import configparser
import psycopg2 as mock_db

@pytest.fixture(scope="session")
def connect_to_mock_database():
    dirname = os.getcwd()
    config = configparser.ConfigParser()
    config.read(os.path.join(dirname, 'tests/assets/mock_dbtool.ini'))
    conn = mock_db.connect(**config['connection'])
    curs = conn.cursor()
    curs.execute(config['create_schema']['new_schema'].replace('@schema_name@', 'test_schema'))
    return curs, config