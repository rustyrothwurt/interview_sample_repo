import pandas as pd

#full method to call to validate and get the csv returned as dict
def convert_csv_to_list(input_file, ingest=False, columns=['val']):
    """
    Method to call to validate and get the csv returned as dictlist
    Args:
        input_file: can be a filepath or request.files.get('file') from flask
        ingest: boolean - currently unused as this would be more useful for more columns
        columns: array of column names - same as ingest; not used yet
    Returns:
        list: a list of records as numerics
    Raises:
        ValueError: if validations fail
        ParserError: Pandas specific error indicating bad format
        EmptyDataError: Pandas specific error indicating empty file
        FileNotFoundError: non-existent/bad path to input file
        UnicodeDecodeError: error indicating not a parseable file (e.g., an img)
    """
    df = _parse_csv_to_df(input_file)
    errors = _validate_df(df)
    if len(errors) > 0:
        raise ValueError(errors)
    if ingest:
        return _convert_df_to_dictlist(df, columns=columns)
    else:
        return _get_numerics_list(df)


def _parse_csv_to_df(input_file):
    return pd.read_csv(input_file, header=None)

def _validate_df(df):
    errors = {}
    failed_numerics = _get_failed_numerics(df)
    if (len(failed_numerics)) > 0:
        errors["value_validation"] = {}
        errors["value_validation"]["message"] = f"The input file has bad values"
        errors["value_validation"]["data"] = failed_numerics
    if (df_col_len := len(df.columns)) > 1:
        errors["column_validation"] = {}
        errors["column_validation"]["message"] = f"The input file has too many columns: {df_col_len}"
        errors["column_validation"]["data"] = list(df.columns)
    return errors

def _get_numerics_list(df):
    series_col = df.iloc[:, 0]
    return (pd.to_numeric(series_col, errors='coerce')).to_list()

def _get_failed_numerics(df):
    failed_list = []
    numeric_list = _get_numerics_list(df)
    for idx, l in enumerate(numeric_list):
        if pd.isna(l):
            failed_list.append({idx: l})
    return failed_list


def _convert_df_to_dictlist(df, columns=['val']):
    # df.to_dict(orient='records')
    df.columns = columns
    return df.to_dict(orient='records')
