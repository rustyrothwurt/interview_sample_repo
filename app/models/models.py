import datetime

from sqlalchemy import schema, Column, inspect, ForeignKey, String, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import synonym, relationship, Mapper
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, NUMERIC, INTEGER, TEXT, JSON

from . import mixins

#####################################################
# create bases
######################################################
Base = declarative_base()

class BaseModel(Base, mixins.SerializeInspectMixin):
    __abstract__ = True
    pass
#####################################################
# actual models based on base
######################################################


class IngestionJobs(BaseModel):
    __tablename__ = 'IngestionJobs'
    uid = Column("uid", INTEGER, primary_key=True, autoincrement=True)
    shorttext = Column("shorttext", String(150), unique=True, nullable=False)
    filename = Column("filename", String(150), nullable=False)
    #provided_uid_type = Column("provided_uid_type", ENUM("text", "int", name="provided_uid_enum"), nullable=False, server_default="int")
    #provided_value_type = Column("provided_value_type", ENUM("float", "int", name="provided_value_enum"), nullable=False, server_default="int")
    ingested_date = Column("ingested_date", TIMESTAMP, default=(datetime.datetime.now()))
    benfords_result = Column("benfords_result", TEXT, nullable=True) #retrieve as text > JSON (json.loads(string))
    significance_result = Column("significance_result", TEXT, nullable=True) #retrieve as text > JSON (json.loads(string))
    children = relationship("IngestedData", back_populates="parent", cascade="all, delete, delete-orphan",
                            lazy="joined")


class IngestedData(BaseModel):
    __tablename__ = 'IngestedData'
    uid = Column("uid", INTEGER, primary_key=True, autoincrement=True)
    #provided_uid = Column("provided_uid", TEXT, nullable=True)
    parent_id = Column("parent_id", INTEGER, ForeignKey('IngestionJobs.uid'), nullable=False)
    val = Column("val", NUMERIC, nullable=True)
    parent = relationship("IngestionJobs")



@event.listens_for(Mapper, 'init')
def received_init(target, args, kwargs):
    """Allow initializing nested relationships with dict only"""
    for rel in inspect(target.__class__).relationships:
        if rel.key in kwargs:
            if rel.uselist:
                kwargs[rel.key] = [rel.mapper.class_(**c) for c in kwargs[rel.key]]
            else:
                kwargs[rel.key] = rel.mapper.class_(**kwargs[rel.key])