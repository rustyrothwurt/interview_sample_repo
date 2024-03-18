import json
import os
import io
import unittest
import contextlib
from urllib.parse import urlencode
import logging
from logging import config
from datetime import date

import werkzeug
from flask import jsonify, g, Flask, request, redirect, url_for, render_template, flash, make_response, stream_with_context

from config import logging_config, db_config
from data_access import db_dto
from services import benfords as bf
from services import ingestion as ig
from services import plotly as pl
from tests import suite_runner as sr
from util import common

####################################
# APP INIT
####################################
#ideally this could be moved up a level into an app factory
#uses env variables as well as defaults set in the config module
app = Flask(__name__)
app.config.from_pyfile(os.environ['ENV_FILE_PATH'])
app.config["DB"] = db_config.get_db_config(app.config)
logger = logging.getLogger("app")
config.dictConfig(logging_config.get_app_logging_config(app.config))


####################################
###     context processors      ###
####################################
@app.context_processor
def json_string_processor():
    def get_json(input_string):
        return json.loads(input_string)
    return dict(get_json=get_json)


@app.context_processor
def string_json_processor():
    def get_string(input_json):
        return json.dumps(input_json)
    return dict(get_string=get_string)

@app.context_processor
def path_processor():
    def get_paths(request_path):
        paths = list(p for p in request_path.split('/') if len(p) > 0)
        path_dict = {"page_action":None, "thing_type":None, "thing_id":None}
        if len(paths) > 0:
            path_dict["page_action"] = paths[0]
        if len(paths) > 1:
            path_dict["thing_type"] = paths[1]
        if len(paths) > 2:
            path_dict["thing_id"] = paths[2]
        return path_dict
    return dict(get_paths=get_paths)


####################################
###     template filters        ###
####################################
@app.template_filter('pretty_json')
def pretty_json(value):
    return json.dumps(value, sort_keys=True, indent=4, separators=(',', ': '))

@app.template_filter('last_path')
def last_path(value):
    return value.split('/')[-1:][0]


@app.template_filter('increment_offset')
def increment_offset(base_url, req_args, offset):
    """ app.run.increment_offset: used like...
        the value on the left of the |/pipe is the first arg passed in by default
     {{ request.base_url|decrement_offset(page_data.filters, page_data.filters['offset']) }}"""
    req_args["offset"] = int(offset) + 1
    return f"{base_url}?{urlencode(req_args)}"


@app.template_filter('decrement_offset')
def decrement_offset(base_url, req_args, offset):
    if int(offset) > 0:
        req_args["offset"] = int(offset) - 1
    return f"{base_url}?{urlencode(req_args)}"


@app.template_filter('to_bool')
def to_bool(val):
    if val > 0:
        return "True"
    else:
        return "False"

@app.template_filter('to_int')
def to_int(val):
    return int(val)


####################################
###     error routes        ###
####################################
"""
 TODO: handle the below more elegantly and cleanly (can redirect to one with page data and message)
"""
@app.errorhandler(404)
def not_found(e):
    # note that we set the 404 status explicitly
    page_data = {}
    page_data["message"] = "404: Not Found"
    page_data["data"] = "Go back and try again"
    flash('path not found + {0}'.format(e), 'error')
    return render_template('error.html', page_data=page_data), 404

@app.errorhandler(400)
def bad_request(e):
    # note that we set the 404 status explicitly
    page_data = {}
    page_data["message"] = "400: Bad request"
    page_data["data"] = "Go back and try again"
    flash('path not found + {0}'.format(e), 'error')
    return render_template('error.html', page_data=page_data), 400

@app.errorhandler(403)
def not_allowed(e):
    # note that we set the 404 status explicitly
    page_data = {}
    page_data["message"] = "403: Not Allowed"
    page_data["data"] = "Go back and try again"
    flash('path not found + {0}'.format(e), 'error')
    return render_template('error.html', page_data=page_data), 403

@app.errorhandler(werkzeug.exceptions.BadRequest)
def handle_other_bad_request(e):
    page_data = {}
    page_data["message"] = f"Other exception: {e}"
    page_data["data"] = "Go back and try again"
    flash('path not found', 'error')
    return render_template('error.html', page_data=page_data)


####################################
###     main routes        ###
####################################
@app.route("/")
@app.route("/index")
def show_home():
    """
    app.run.show_home  - / or /index
    :return: renders the app/templates/index.html file
    """
    return render_template("index.html")

@app.route("/admin/db")
def setup_db():
    """
    app.run.show_home  - / or /index
    :return: renders the app/templates/index.html file
    """
    resp = db_dto.setup_db()
    if resp["data"] is not None:
        flash(resp["data"], "success")
    else:
        flash("Encountered error when creating tables. Check pgadmin at http://localhost:5050/browser/#", "warning")
    return render_template("index.html")


@app.route("/admin/tests")
def run_tests():
    page_data = {}
    page_data["thing_type"] = "Tests"
    page_data["data"] = "Error running tests"
    suite = sr.get_test_suite()
    suite.countTestCases()
    with io.StringIO() as buf:
        with contextlib.redirect_stdout(buf):
            unittest.TextTestRunner(verbosity=2, stream=buf).run(suite)
        response = buf.getvalue()
    page_data["data"] = response
    if "FAIL" in response:
        flash("Ran {0} tests and encountered failures. Check the app log.".format(suite.countTestCases()), "warning")
    else:
        flash("Ran {0} tests OK.".format(suite.countTestCases()), "success")
    return render_template("admin.html", page_data=page_data)


# a request_obj has:# uid, parent_id, shorttext, "offset":None,
@app.route("/view/<string:thing_type>", methods=['GET'])
@app.route("/view/<string:thing_type>/<int:thing_id>", methods=['GET'])
def view(thing_type="jobs", thing_id=None, **kwargs):
    page_data = {}
    if "job" in thing_type:
        page_data["obj"] = "IngestionJobs"
    elif "data" in thing_type:
        page_data["obj"] = "IngestedData"
    page_data["data"] = None
    page_data["request_obj"] = {}
    page_data["request_obj"].update(request.args)
    if request.method == 'GET':
        if thing_id is not None:
            page_data["request_obj"]["uid"] = thing_id
            resp = db_dto.get_record(page_data["obj"], page_data["request_obj"])
            if len(resp.get("data", None)) == 1 and resp["data"][0].get("benfords_result"):
                benfords_result = json.loads(resp["data"][0].get("benfords_result"))
                page_data["significance"] = json.loads(resp["data"][0].get("significance_result"))
                page_data["results"] = benfords_result
                page_data["graphJSON"] = pl.dump_plotly_data(pl.get_graph(benfords_result))
        else:
            resp = db_dto.query_records(page_data["obj"], page_data["request_obj"])
        flash("Queried data from the DB. Found {0} results out of {1}".format(len(resp["data"]), resp["count"]), "info")
    page_data["count"] = resp.get("count")
    page_data["data"] = resp.get("data")
    page_data["request_obj"] = resp.get("query_obj")
    return render_template('view.html', page_data=page_data)


@app.route("/create/jobs", methods=['GET', 'POST'])
def create():
    page_data = {}
    page_data["obj"] = {}
    page_data["data"] = None
    page_data["results"] = []
    page_data["significance"] = []
    page_data["graphJSON"] = None
    page_data["request_obj"] = {} #request args
    page_data["request_obj"]["filters"] = [] #form data
    page_data["request_obj"]["args"] = {}  # form data
    app.logger.info(page_data)
    if request.method == "POST":
        app.logger.info("Uploading a file to view the results for")
        f = request.files.get('ingesteddata')
        if f is None:
            flash("input file is missing", "error")
        else:
            page_data["obj"]["filename"] = f.filename
            savetodb = request.form.get('savetodb', False)
            valuelist = ig.convert_csv_to_list(f)
            app.logger.debug("value list: {0}".format(valuelist))
            benfords_result = bf.validate_and_calculate(valuelist)
            significance_result = bf.test_significance(benfords_result)
            app.logger.debug("benfords results: {0}".format(benfords_result))
            app.logger.debug("significance results: {0}".format(significance_result))
            page_data["results"] = benfords_result
            page_data["significance"] = significance_result
            page_data["graphJSON"] = pl.dump_plotly_data(pl.get_graph(benfords_result))
            if savetodb:
                page_data["obj"]["shorttext"] = request.form.get('shorttext')
                if len(page_data["obj"]["shorttext"]) < 6 or len(page_data["obj"]["shorttext"]) > 150:
                    flash("Short text field does not fit length requirements of 6-150. Did not save to database.", "warning")
                else:
                    # this is specifically to dump to the database
                    page_data["obj"]["benfords_result"] = json.dumps(benfords_result)
                    page_data["obj"]["significance_result"] = json.dumps(significance_result)
                    page_data["obj"]["children"] = list({'val': n} for n in valuelist)
                    add_resp = db_dto.add_record("IngestionJobs", page_data["obj"])
                    flash("Created {0} records ".format(add_resp["count"]), "success")
        return render_template('view.html', page_data=page_data)
    else:
        return render_template("create.html", page_data=page_data)


####################################
# MAIN START APP
####################################
if __name__ == '__main__':
    print (os.environ['FLASK_RUN_HOST'])
    #host=app.config.FLASK_RUN_HOST, port=app.config.FLASK_RUN_PORT
    app.run(host=os.environ['FLASK_RUN_HOST'], port=os.environ['FLASK_RUN_PORT'] )

