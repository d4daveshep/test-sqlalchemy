from sqlalchemy import Integer, ForeignKey, String, Column
from sqlalchemy.orm import DeclarativeBase, mapped_column
from sqlalchemy.orm import relationship


class Base(DeclarativeBase):
    pass


class Customer(Base):
    __tablename__ = "customer"
    id = mapped_column(Integer, primary_key=True)
    name = mapped_column(String)

    billing_address_id = mapped_column(Integer, ForeignKey("address.id"))
    shipping_address_id = mapped_column(Integer, ForeignKey("address.id"))

    billing_address = relationship("Address", foreign_keys=[billing_address_id])
    shipping_address = relationship("Address", foreign_keys=[shipping_address_id])


class Address(Base):
    __tablename__ = "address"
    id = mapped_column(Integer, primary_key=True)
    street = mapped_column(String)
    city = mapped_column(String)
    state = mapped_column(String)
    zip = mapped_column(String)