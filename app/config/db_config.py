def get_db_config(config):
    db_dict_cfg = {}
    required_db_vars = ["POSTGRES_USER", "POSTGRES_PASSWORD", "POSTGRES_HOST","POSTGRES_PORT"]
    has_all = all([config.get(c, False) for c in required_db_vars])
    if has_all:
        db_dict_cfg["DB_USER"] = config.get("POSTGRES_USER")
        db_dict_cfg["DB_PASSWORD"] = config.get("POSTGRES_PASSWORD")
        db_dict_cfg["DB_HOST"] = config.get("POSTGRES_HOST")
        db_dict_cfg["DB_PORT"] = (config.get("POSTGRES_PORT").split(":"))[0]
        db_dict_cfg["DB_NAME"] = config.get("POSTGRES_DB")
    else:
        raise ValueError("Missing a database config item.")
    return db_dict_cfg

