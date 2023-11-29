import pytest
SCHEMA_NAME = 'test_schema'

def test_charity_table(connect_to_mock_database):
    (curs, config) = connect_to_mock_database
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

    # Insert single entry and assert presence
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'charity'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 1)