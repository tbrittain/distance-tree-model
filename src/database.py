from sqlalchemy import MetaData, Table, Column, Integer, String, ForeignKey, create_engine

if __name__ == '__main__':
    sql_engine = create_engine('sqlite:///database.sqlite', echo=True)

    metadata = MetaData()
    users = Table('users', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('username', String),
                  Column('password', String))
    posts = Table('posts', metadata,
                  Column('id', Integer, primary_key=True),
                  Column('title', String),
                  Column('content', String),
                  Column('user_id', Integer, ForeignKey('users.id')))
    comments = Table('comments', metadata,
                     Column('id', Integer, primary_key=True),
                     Column('content', String),
                     Column('user_id', Integer, ForeignKey('users.id')),
                     Column('post_id', Integer, ForeignKey('posts.id')))
    metadata.create_all(sql_engine)

