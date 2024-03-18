from services.db_service import DBQueryService


def setup_db():
    # find result in returned_obj["data"]
    db_service = DBQueryService()
    return db_service.do_db_query("setup", obj=None, request_obj=None)


def verify_db():
    # find result in returned_obj["data"] return_obj["data"] = None
    db_service = DBQueryService()
    return db_service.do_db_query("verify", obj=None, request_obj=None)


def add_record(obj, data, merge=True):
    # find result in returned_obj["data"], returned_obj["count"]
    db_service = DBQueryService()
    if merge:
        return db_service.do_db_query("merge", obj=obj, request_obj=data)
    else:
        return db_service.do_db_query("add", obj=obj, request_obj=data)


def query_records(obj, request_obj):
    db_service = DBQueryService()
    return db_service.do_db_query("query", obj=obj, request_obj=request_obj)


def get_record(obj, request_obj):
    db_service = DBQueryService()
    return db_service.do_db_query("get", obj=obj, request_obj=request_obj)