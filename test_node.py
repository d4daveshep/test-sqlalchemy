import pytest
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from entities import Node, Base


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


@pytest.fixture()
def session_with_3_nodes(session):
    andrew = Node(name="Andrew Lindesay")
    david = Node(name="David Rawson")
    robin = Node(name="Robin Southgate")
    session.add_all([andrew, david, robin])
    session.commit()

    yield session


def test_create_node(session):
    node_1 = Node(name="Andrew Lindesay")
    session.add(node_1)
    session.commit()

    assert node_1.id
    assert node_1.name == "Andrew Lindesay"
    assert node_1.__repr__() == f"Node(id={node_1.id}, name='{node_1.name}')"


def test_read_node(session_with_3_nodes):
    select_stmt = select(Node).where(Node.name.in_(["Andrew Lindesay"]))
    nodes = [node for node in session_with_3_nodes.scalars(select_stmt)]
    assert len(nodes) == 1
    assert nodes[0].name == "Andrew Lindesay"

    select_stmt = select(Node).where(Node.name.contains("David"))
    nodes = [node for node in session_with_3_nodes.scalars(select_stmt)]
    assert len(nodes) == 1
    assert nodes[0].name == "David Rawson"


def test_select_node_case_insensitive(session_with_3_nodes):
    select_stmt = select(Node).where(Node.name.ilike("%robin%"))
    robin = session_with_3_nodes.scalars(select_stmt).one()
    assert robin.name == "Robin Southgate"


def test_cant_read_non_existent_node(session_with_3_nodes):
    select_stmt = select(Node).where(Node.name.contains("Chris"))
    nodes = [node for node in session_with_3_nodes.scalars(select_stmt)]
    assert len(nodes) == 0


def test_update_node(session_with_3_nodes):
    select_stmt = select(Node).where(Node.name.contains("Andrew"))
    andrew = session_with_3_nodes.scalars(select_stmt).one()
    andrew.name = "Andy Linde"
    session_with_3_nodes.commit()

    select_stmt = select(Node).where(Node.name.contains("Andy"))
    andy = session_with_3_nodes.scalars(select_stmt).one()
    assert andy.name == "Andy Linde"


def test_delete_node(session_with_3_nodes):
    select_stmt = select(Node).where(Node.name.contains("David"))
    david = session_with_3_nodes.scalars(select_stmt).one()
    session_with_3_nodes.delete(david)
    session_with_3_nodes.commit()

    select_stmt = select(Node)
    assert len(session_with_3_nodes.scalars(select_stmt).all()) == 2


