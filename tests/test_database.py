import pytest
from datetime import datetime

SCHEMA_NAME = 'test_schema'

def test_inserting_single_item_into_charity_table(connect_to_database, create_charity_table):
    (curs, config) = connect_to_database
    # Charity table should initially be empty
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


def test_multiple_items_into_charity_table(connect_to_database, create_charity_table):
    (curs, config) = connect_to_database
    # Insert three entries into the charity table
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['Feed', 312]
    )
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['Food Bank', 222]
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'charity'
    ))
    rec_all = curs.fetchall()
    assert(len(rec_all) == 3)

    # Check the filter by name works
    curs.execute(config['query']['select_charity_by_name'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP']
    )
    rec_named = curs.fetchall()
    assert(len(rec_named) == 1)

    # Check the filter by number works
    curs.execute(config['query']['select_charity_by_number'].replace(
        '@schema_name@', SCHEMA_NAME), [312]
    )
    rec_number = curs.fetchall()
    assert(len(rec_number) == 1)


def test_inserting_single_item_into_schedule_table(connect_to_database, create_schedule_table):
    (curs, config) = connect_to_database
    # Set up charity table with at least one entry
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )

    # Schedule table should initially be empty
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 0)

    # Insert single entry into schedule table and assert presence
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Monday', 'Afternoon', 'Chelsea']
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 1)


def test_inserting_multiple_items_into_schedule_table(connect_to_database, create_schedule_table):
    (curs, config) = connect_to_database
    # Set up charity table with multiple entities
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['Feed', 312]
    )

    # Insert four entries into schedule table and assert presence
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Monday', 'Afternoon', 'Chelsea']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Wednesday', 'Morning', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [312, 'Wednesday', 'Morning', 'Southwark']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [312, 'Tuesday', 'Evening', 'Camden']
    )
    curs.execute(config['insert_into']['schedule_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Wednesday', 'Afternoon', 'Ealing']
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'schedule'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 5)

    # Check the filter by day of the week works
    curs.execute(config['query']['select_schedule_by_day'].replace(
        '@schema_name@', SCHEMA_NAME), ['Wednesday']
    )
    rec_day = curs.fetchall()
    assert(len(rec_day) == 3)

    # Check the filter by time works
    curs.execute(config['query']['select_schedule_by_time'].replace(
        '@schema_name@', SCHEMA_NAME), ['Afternoon']
    )
    rec_time = curs.fetchall()
    assert(len(rec_time) == 2) 

    # Check the filter by day and time works
    curs.execute(config['query']['select_schedule_by_day_and_time'].replace(
        '@schema_name@', SCHEMA_NAME), ['Wednesday', 'Morning']
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 2)   

    # Check the filter by location works
    curs.execute(config['query']['select_schedule_by_location'].replace(
        '@schema_name@', SCHEMA_NAME), ['Camden']
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 2)

    # Check the filter by day and location works
    curs.execute(config['query']['select_schedule_by_day_and_location'].replace(
        '@schema_name@', SCHEMA_NAME), ['Wednesday', 'Camden']
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 1) 

    # Check the filter by time and location works
    curs.execute(config['query']['select_schedule_by_time_and_location'].replace(
        '@schema_name@', SCHEMA_NAME), ['Morning', 'Southwark']
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 1)    

    # Check the filter by day and time and location works
    curs.execute(config['query']['select_schedule_by_day_and_time_and_location'].replace(
        '@schema_name@', SCHEMA_NAME), ['Wednesday', 'Morning', 'Camden']
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 1)  

    # Check the filter by charity number works
    curs.execute(config['query']['select_schedule_by_charity_number'].replace(
        '@schema_name@', SCHEMA_NAME), [123]
    )
    rec_location = curs.fetchall()
    assert(len(rec_location) == 3)

    ## TODO: Add a filter to search by charity name? although may not be unique... ## 


def test_inserting_single_item_into_message_table(connect_to_database, create_message_table):
    (curs, config) = connect_to_database
    # Set up charity table with at least one entry
    curs.execute(config['insert_into']['charity_table'].replace(
        '@schema_name@', SCHEMA_NAME), ['SVP', 123]
    )

    # Message table should initially be empty
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'message'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 0)

    # Insert single entry and assert presence
    example_datetime = datetime(2023, 11, 29, 12, 00, 00)
    curs.execute(config['insert_into']['message_table'].replace(
        '@schema_name@', SCHEMA_NAME), [123, 'Sample message', example_datetime]
    )
    curs.execute(config['query']['select_all'].replace(
        '@schema_name@', SCHEMA_NAME).replace(
        '@table_name@', 'message'
    ))
    rec = curs.fetchall()
    assert(len(rec) == 1)

