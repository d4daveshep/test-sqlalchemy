import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from entities import Node, Base, Connection


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


def test_create_connection(session):
    conn_1 = Connection(subject=Node(name="Andrew"), name="has title", target=Node(name="Chief Engineer"))
    session.add(conn_1)
    session.commit()
