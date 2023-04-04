import pytest
from sqlalchemy import create_engine, select, delete
from sqlalchemy.orm import Session

from entities import Node, Base, Connection


@pytest.fixture()
def session():
    engine = create_engine("sqlite://", echo=True)

    Base.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

        pass


@pytest.fixture()
def session_with_nodes_and_connections(session):
    # people
    andrew = Node(name="Andrew Lindesay")
    david = Node(name="David Rawson")
    robin = Node(name="Robin Southgate")

    # roles
    chief = Node(name="Chief Engineer")
    fe_pl = Node(name="Front End Practice Lead")

    # skills
    java = Node(name="Java")
    angular = Node(name="Angular")
    react = Node(name="React")
    android = Node(name="Android")
    spring_boot = Node(name="SpringBoot")

    # customers
    twg = Node(name="The Warehouse Group")
    cdx = Node(name="CountdownX")
    westpac = Node(name="Westpac NZ")
    gdt = Node(name="Global Dairy Trade")

    andrew_chief = Connection(subject=andrew, name="has title", target=chief)
    andrew_java = Connection(subject=andrew, name="knows", target=java)
    andrew_spring_boot = Connection(subject=andrew, name="knows", target=spring_boot)
    andrew_twg = Connection(subject=andrew, name="worked on", target=twg)
    andrew_gdt = Connection(subject=andrew, name="worked on", target=gdt)

    david_lead = Connection(subject=david, name="has title", target=fe_pl)
    david_java = Connection(subject=david, name="knows", target=java)
    david_android = Connection(subject=david, name="knows", target=android)
    david_westpac = Connection(subject=david, name="worked on", target=westpac)

    robin_chief = Connection(subject=robin, name="has title", target=chief)
    robin_angular = Connection(subject=robin, name="knows", target=angular)
    robin_react = Connection(subject=robin, name="knows", target=react)
    robin_cdx = Connection(subject=robin, name="worked on", target=cdx)
    robin_gdt = Connection(subject=robin, name="worked on", target=gdt)

    session.add_all([andrew_chief, andrew_java, andrew_spring_boot, andrew_twg, andrew_gdt,
                     david_lead, david_java, david_android, david_westpac,
                     robin_chief, robin_angular, robin_react, robin_cdx, robin_gdt
                     ])
    session.commit()

    yield session


def test_create_connection(session):
    conn_1 = Connection(subject=Node(name="Andrew"), name="has title", target=Node(name="Chief Engineer"))
    session.add(conn_1)
    session.commit()


def test_fixture(session_with_nodes_and_connections):
    select_all_nodes = select(Node)
    nodes = session_with_nodes_and_connections.scalars(select_all_nodes).all()
    assert len(nodes) == 14

    select_all_connections = select(Connection)
    connections = session_with_nodes_and_connections.scalars(select_all_connections).all()
    assert len(connections) == 14


def test_read_connections_by_name(session_with_nodes_and_connections):
    select_connection = select(Connection).where(Connection.name.ilike("%title%"))
    conns = session_with_nodes_and_connections.scalars(select_connection).all()
    assert len(conns) == 3
    for conn in session_with_nodes_and_connections.scalars(select_connection):
        conn_name = conn.name
        assert "title" in conn_name


def test_read_connections_by_subject(session_with_nodes_and_connections):
    select_stmt = select(Connection).join(
        Connection.subject.and_(Node.id == Connection.subject_id).and_(Node.name.ilike("%andrew%")))
    conns = session_with_nodes_and_connections.scalars(select_stmt).all()
    assert len(conns) == 5
    for conn in session_with_nodes_and_connections.scalars(select_stmt):
        subject_name = conn.subject.name
        assert "andrew".casefold() in subject_name.casefold()


def test_delete_connection_doesnt_delete_node(session_with_nodes_and_connections):
    select_connection = select(Connection).where(Connection.name.ilike("%title%"))
    conns = session_with_nodes_and_connections.scalars(select_connection).all()
    assert len(conns) == 3

    conn = session_with_nodes_and_connections.scalars(select_connection).first()
    subject = conn.subject
    target = conn.target

    session_with_nodes_and_connections.delete(conn)
    session_with_nodes_and_connections.commit()

    conns = session_with_nodes_and_connections.scalars(select_connection).all()
    assert len(conns) == 2

    assert session_with_nodes_and_connections.get(Node, subject.id)
    assert session_with_nodes_and_connections.get(Node, target.id)


def test_delete_node_cascades_deletes_to_connections(session_with_nodes_and_connections):
    select_robins_connections = select(Connection).join(
        Connection.subject.and_(Node.id == Connection.subject_id).and_(Node.name.ilike("%robin%")))
    conns = session_with_nodes_and_connections.scalars(select_robins_connections).all()
    assert len(conns) == 5

    select_robin = select(Node).where(Node.name.ilike("%robin%"))
    robin = session_with_nodes_and_connections.scalars(select_robin).one()
    assert robin.name == "Robin Southgate"

    session_with_nodes_and_connections.delete(robin)
    session_with_nodes_and_connections.commit()

    conns = session_with_nodes_and_connections.scalars(select_robins_connections).all()
    assert len(conns) == 0

    delete_stmt = delete(Connection).where(Connection.subject_id == robin.id)
    result = session_with_nodes_and_connections.execute(delete_stmt)
    assert result.rowcount == 5
    delete_stmt = delete(Connection).where(Connection.target_id == robin.id)
    result = session_with_nodes_and_connections.execute(delete_stmt)
    assert result.rowcount == 0

    select_all_connections = select(Connection)
    connections = session_with_nodes_and_connections.scalars(select_all_connections).all()
    assert len(connections) == 9

