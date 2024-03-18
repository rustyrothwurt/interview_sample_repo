from functools import wraps
import time
from datetime import datetime
import importlib


from sqlalchemy import schema, Table, text, exc, create_engine, func, select, desc, asc, between, case, and_, or_
from sqlalchemy.orm import Session, Query
from sqlalchemy.sql.expression import literal_column, cast
from sqlalchemy.pool import NullPool
from sqlalchemy.exc import OperationalError, InvalidRequestError, TimeoutError, DisconnectionError, \
	ResourceClosedError, InternalError, IntegrityError

from flask import current_app

from util import common
from models import models

def _retry_query(allowed_exceptions=(TimeoutError, ConnectionError), tries=5, delay=5):
	def deco_retry(f):
		@wraps(f)
		def f_retry(*args, **kwargs):
			mtries, mdelay = tries, delay
			while mtries > 1:
				try:
					return f(*args, **kwargs)
				except allowed_exceptions as oe:
					current_app.logger.warning("Encountered error: {0} . Retrying in {1} seconds".format(str(oe), mdelay))
					time.sleep(mdelay)
					mtries -= 1
					if mtries == 0:
						current_app.logger.error("Encountered error: {0}. Out of retries".format(str(oe)))
			return f(*args, **kwargs)
		return f_retry
	return deco_retry


class DBQueryService(object):
	def __init__(self):
		cfg = current_app.config.get("DB")
		#postgresql://postgres:p3wrd@postgres:5432/postgres
		self.connection_string = "postgresql://{0}:{1}@{2}:{3}/{4}".format(
			cfg["DB_USER"], cfg["DB_PASSWORD"], cfg["DB_HOST"], cfg["DB_PORT"], cfg["DB_NAME"])
		self.default_base_class = "Base"
		self.default_model_module = "models.models"
		self.engine = create_engine(self.connection_string, poolclass=NullPool, echo=True)
		#self.metadata = schema.MetaData(bind=self.engine)

	def _rollback_session(self):
		self.session.rollback()

	def _close_session(self):
		self.session.close()

	def _get_table_class(self, base_class=None, module_name=None):
		if base_class is None:
			base_class = self.default_base_class
		if module_name is None:
			module_name = self.default_model_module
		return getattr(importlib.import_module(module_name), base_class)

	def _list_all_tables(self, base_class=None, module_name=None):
		create_base = self._get_table_class(base_class=base_class, module_name=module_name)
		return list(create_base.metadata.tables.keys())

	def _execute_statement(self, exec_statement):
		#Upon successful operation, the Transaction is committed.
		# #If an error is raised, the Transaction is rolled back.
		with self.engine.begin() as connection:
			return connection.execute(exec_statement)

	def _truncate_table(self, obj):
		self._execute_statement(f"TRUNCATE TABLE {obj}")

	def _create_tables(self, base_class=None, module_name=None, tables=[]):
		create_base = self._get_table_class(base_class=base_class, module_name=module_name)
		if tables is not None:
			tables = [].extend(tables)
			create_base.metadata.create_all(self.engine, tables=tables)
		else:
			create_base.metadata.create_all(self.engine)

	def _drop_tables(self, base_class=None, module_name=None, tables=[]):
		create_base = self._get_table_class(base_class=base_class, module_name=module_name)
		if tables is not None:
			tables = [].extend(tables)
			create_base.metadata.drop_all(self.engine, tables=tables)
		else:
			create_base.metadata.drop_all(self.engine)

	def _get_records_query(self, table_name, query_args):
		current_app.logger.info(query_args)
		table_obj = self._get_table_class(base_class=table_name)
		current_app.logger.debug('Getting from {0}'.format(table_name))
		query = Query([table_obj])
		filter_eq_fields = {}
		filter_like_fields = []
		for k,v in query_args.items():
			if k == "uid" or k == "parent_id":
				filter_eq_fields[k] = v
			elif k == "shorttext":
				fl = {}
				fl["field"] = k
				fl["value"] = v
				filter_like_fields.append(fl)
		if filter_eq_fields:
			query = query.filter_by(**filter_eq_fields)
		for fl in filter_like_fields:
			query = query.filter(literal_column(fl["field"]).like("%{0}%".format(fl["value"])))
		return query


	def _make_add_record(self, obj, record):
		"""
		Adds a new record from an input dictionary that has optional nested children field
		Args:
			obj: string representing the parent table name
			record: a dictionary with the parent record values and nested children
			session: provided by the parent function
			merge: flag to indicate upsert or new

		Returns:

		"""
		table_obj = self._get_table_class(obj)
		current_app.logger.info('Adding or merging into {0}'.format(table_obj))
		if record is not None:
			if isinstance(record, dict):
				record_to_add = table_obj(**record)
			else:
				record_to_add = table_obj(record)
			return record_to_add
		else:
			return None

	@_retry_query()
	def do_db_query(self, method, obj=None, request_obj=None):
		"""

		Args:
			method:
			obj:
			request_obj:

		Returns:

		Todo:
			* anything returned from a function should be the same, not like this.
			* refactor so you can return objects elegantly from a much smaller function
			* the returned object itself should be its own class/object
			* find a better way to update the front-end/request params/args without having to overwrite them here

		"""
		return_obj = {}
		return_obj["data"] = None
		return_obj["count"] = None
		return_obj["query_obj"] = {}
		# with session is already a context manager, so not okay exits
		# will cause the session to rollback automatically
		with Session(self.engine) as session, session.begin():
			if method == "setup":
				self._create_tables()
				return_obj["data"] = "Created tables {0}".format(self._list_all_tables())
			elif method == "verify":
				return_obj["data"] = self._list_all_tables()
			elif method == "query" or method == "get":
				return_obj["query_obj"] = request_obj
				query = self._get_records_query(obj, request_obj)
				count_result = query.with_session(session).count()
				return_obj["count"] = count_result
				if count_result >= 1000:
					query = query.limit(1000)
					if request_obj.get("offset", None) is None:
						new_offset = 0
					else:
						new_offset = request_obj.get('offset')
					query = query.offset(int(new_offset) * 1000)
					return_obj["query_obj"]["offset"] = new_offset
				elif count_result < 1000:
					return_obj["query_obj"]["offset"] = None
				if (sortby := request_obj.get("sortby", None)) is not None:
					#this chunk is not used.
					order = request_obj.get("order", "desc")
					sort = desc(sortby) if order == "desc" else asc(sortby)
					return_obj["query_obj"]["order"] = order
					return_obj["query_obj"]["sortby"] = sortby
					query = query.order_by(sort)
				qres = query.with_session(session).all()
				if method == "query":
					return_obj["data"] = list(q.to_dict(nested=False) for q in qres)
				else:
					return_obj["data"] = [qres[0].to_dict(nested=True)]
			elif method in ["add", "merge"]:
				record_to_add = self._make_add_record(obj, request_obj)
				current_app.logger.info("trying to make a record: {0}".format(record_to_add))
				if method == "merge":
					current_app.logger.debug('merging/upserting this record: {0}'.format(record_to_add))
					session.merge(record_to_add)
				else:
					current_app.logger.debug('creating this record: {0}'.format(record_to_add))
					session.add(record_to_add)
				session.flush()
				return_obj["data"] = "created new record"
				session.commit()
				return_obj["count"] = 1
			else:
				raise ValueError("Did not provide valid db action.")
			return return_obj
