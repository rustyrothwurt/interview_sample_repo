import datetime
import json

from sqlalchemy import schema, Column, inspect, ForeignKey, String, asc, desc
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from sqlalchemy.orm import synonym, relationship, Bundle, RelationshipProperty
from sqlalchemy.dialects.postgresql import ENUM, TIMESTAMP, NUMERIC, INTEGER, TEXT
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.orm import selectinload, joinedload, Load

# for logging
from flask import current_app


class classproperty(object):
    def __init__(self, fget):
        self.fget = fget

    def __get__(self, owner_self, owner_cls):
        return self.fget(owner_cls)


class InspectionMixin(object):
    __abstract__ = True

    @classproperty
    def columns(cls):
        return inspect(cls).columns.keys()

    @classproperty
    def primary_keys_full(cls):
        mapper = cls.__mapper__
        return [
            mapper.get_property_by_column(column) for column in mapper.primary_key
        ]

    @classproperty
    def synonyms_list(cls):
        return list(inspect(cls).synonyms)

    @classproperty
    def synonyms(cls):
        syn_dict = {}
        for s in list(inspect(cls).synonyms):
            syn_dict[s.name] = s.class_attribute.key
        return syn_dict

    @classproperty
    def primary_keys(cls):
        # (User.__mapper__.primary_key)[0].name)
        return [pk.name for pk in list(cls.__mapper__.primary_key)]

    @classproperty
    def relations(cls):
        """Return a `list` of relationship names or the given model
        """
        return [c.key for c in cls.__mapper__.iterate_properties if isinstance(c, RelationshipProperty)]

    @classproperty
    def settable_relations(cls):
        """Return a `list` of relationship names or the given model
        """
        dict_list = []
        for r in cls.relations:
            print(r)
            d = {}
            if getattr(cls, r).property.viewonly is False:
                cl = getattr(cls, r)
                d["cls"] = cl
                d["key"] = r
                dict_list.append(d)
        return dict_list

    @classproperty
    def hybrid_properties(cls):
        items = inspect(cls).all_orm_descriptors
        return [item.__name__ for item in items
                if type(item) == hybrid_property]

    @classproperty
    def hybrid_methods_full(cls):
        items = inspect(cls).all_orm_descriptors
        return {item.func.__name__: item
                for item in items if type(item) == hybrid_method}

    @classproperty
    def hybrid_methods(cls):
        return list(cls.hybrid_methods_full.keys())


class SerializeInspectMixin(InspectionMixin):
    """Mixin to make model serializable."""

    __abstract__ = True

    @classmethod
    def validate_dict(cls, obj):
        new_obj = {}
        these_keys = []
        these_keys.extend(inspect(cls).columns.keys())
        these_keys.extend([s.class_attribute.key for s in inspect(cls).synonyms])
        if isinstance(obj, dict):
            new_obj = obj.copy()
            for k in obj.keys():
                if k in these_keys:
                    new_obj.pop(k)
        return new_obj

    @classmethod
    def from_dict(cls, obj):
        new_obj = {}
        these_keys = []
        these_keys.extend(inspect(cls).columns.keys())
        these_keys.extend([s.class_attribute.key for s in inspect(cls).synonyms])
        if isinstance(obj, dict):
            for k in obj.keys():
                if k in these_keys:
                    new_obj[k] = obj[k]
        return cls(**new_obj)

    @classmethod
    def from_json_str(cls, obj):
        json_dict = json.loads(obj)
        return cls(**json_dict)

    # get this object as a nested dictionary
    def to_dict(self, nested=True, hybrid_attributes=False):
        """Return dict object with model's data."""
        result = dict()
        for key in self.columns:
            result[key] = getattr(self, key)

        if hybrid_attributes:
            for key in self.hybrid_properties:
                result[key] = getattr(self, key)

        if nested:
            for key in self.relations:
                obj = getattr(self, key)
                if isinstance(obj, SerializeInspectMixin):
                    result[key] = obj.to_dict(nested=False, hybrid_attributes=hybrid_attributes)
                else:
                    try:
                        iter_check = iter(obj)
                        result[key] = [o.to_dict(nested=False, hybrid_attributes=hybrid_attributes) for o in obj]
                    except TypeError as e:
                        current_app.logger.warning("not an iterable")
                        pass
        return result

