from sqlalchemy import MetaData, Table, Column, String, create_engine, Numeric, DateTime
from datetime import datetime
from .location import Location

sql_engine = create_engine('sqlite:///database.sqlite', echo=True)


def create_database():
    metadata = MetaData()
    Table('locations', metadata,
          Column('id', String, primary_key=True),
          Column('name', String),
          Column('latitude', Numeric),
          Column('longitude', Numeric),
          Column('added_at', DateTime),
          Column('description', String)
          )
    metadata.create_all(sql_engine)


def insert_location(location: Location) -> bool:
    with sql_engine.connect() as connection:
        connection.execute(
            'INSERT INTO locations (id, name, description, latitude, longitude, added_at) VALUES (?, ?, ?, ?, ?, ?)',
            (
                location.location_id,
                location.name,
                location.description,
                location.latitude,
                location.longitude,
                datetime.now()
            )
        )

    return True


def get_locations() -> list:
    with sql_engine.connect() as connection:
        result = connection.execute('SELECT * FROM locations')
        return [
            Location(
                latitude=row[2],
                longitude=row[3],
                name=row[1],
                location_id=row[0],
                description=row[5])
            for row in result
        ]


def get_location_by_id(location_id: str) -> Location:
    with sql_engine.connect() as connection:
        result = connection.execute('SELECT * FROM locations WHERE id = ?', location_id).fetchone()
        if result is not None:
            return Location(latitude=result[2], longitude=result[3], name=result[1], location_id=result[0])
        else:
            return None


def delete_location_by_id(location_id: str) -> bool:
    with sql_engine.connect() as connection:
        execution_result = connection.execute('DELETE FROM locations WHERE id = ?', location_id)

    return execution_result.rowcount > 0
