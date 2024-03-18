# Interview Challenges
*see [tracebacks.md](./tracebacks.md) and [widgets.md](./widgets.md) for answers to the other challenges*
## Project Objective: Benford's Law 
Create a web application that
1) can ingest the attached example file 
(see modified file at: [census_2009b.txt](./app/static/resources/census_2009b.txt)) 
and any other flat file with a viable target column.
2) validates Benford’s assertion based on the '7_2009' column in the 
supplied file 
3) Outputs back to the user a graph of the observed distribution of 
numbers with an overlay of the expected distribution of numbers.
4) The output should also inform the user of whether the observed 
data matches the expected data distribution. 
5) The delivered package should contain a docker file that allows 
us to docker run the application...
6) Bonus points for automated tests. 
7) Stretch challenge: 
persist the uploaded information to a database so a user 
can come to the application and browse through datasets 
uploaded by other users. 
No user authentication/user management is required here
---
# Building + Setup
## Update the .env and Config Files (opt.)
The `.env` file found in the app/env folder has most of the environment
variables you need to set up already filled in.
There are also hard-coded values for logging in the app/config folder
in `config.py`.

**Possible improvements** 
* move hard-coded values into one or two (secrets in one file,  public values in another)
* enable initialization of Flask `app` via factory method to enable flexible environments
## Build with docker-compose
Save this directory somewhere, unzip if necessary.
If this is your first time running it, 
cd into the `app` folder, then run:
```shell
docker-compose --env-file=./env/.env up --build
```
otherwise you can run:
```shell
docker-compose --env-file=./env/.env up
```

## Create the Tables
If the above was successful, open your browser to [localhost:6050](http://localhost:6050)

Once you first run the app, you need to create the tables using the
button provided. This sends a GET to `/admin/db`, and you should get
a green alert bar if it is successful.

## pgAdmin Setup
Access pgAdmin at [localhost:5050](http://localhost:5050/browser/#).
Check the `env/.env` file for the pgAdmin user email
and password (l7db_user@l7db.com and l7db_password).
)

Connect to the server by clicking on Server (on the left), 
then give it a name, and the host should be `host.docker.internal` with port `5432`,
and use postgres user and password from the .env file 
(l7db_user, l7db_password).

**Future/Possible improvements** 
Future improvements would include using Alembic or other
libraries for real migrations and setup.

## Run the unittests
Also on the homepage is a button for running tests (`/admin/tests`).
This is a limited number of unittests created to fit the 
POC nature of this project. The output that would normally be
viewable in the console will appear as a string in the page.

**Future/Possible improvements** 

As this app only has a limited number of tests, the first step would
be increasing coverage.
After that testing could be expanded by using other testing libraries
such as Selenium for UI testing, API/endpoint testing, etc. as well as 
adding missing class, method, and module docs along with examples to enable tests to be run using `doctest` (see
example below).
```python
def example_generator(n):
    """Generators have a ``Yields`` section instead of a ``Returns`` section.
    Args:
        n (int): The upper limit of the range to generate, from 0 to `n` - 1.=
    Yields:
        int: The next number in the range of 0 to `n` - 1.
    Examples:
        Examples should be written in doctest format, and should illustrate how
        to use the function.

        >>> print([i for i in example_generator(4)])
        [0, 1, 2, 3]
    """
```
# Using the App
## Upload a file
If you go to create/upload from the homepage, you can upload a file
and choose to save it to the database; the instructions are at the top.

This was implemented as simply as possible for this POC as
user-submitted file uploads can get complicated.

To try it out, you can upload one of the two test files in
`/app/static/resources`:
* [world_pop_2015.csv](./app/static/resources/world_pop_2015.csv)
* [census_2009b.txt](./app/static/resources/census_2009b.txt)

## View the results
Once you upload data, you should see two Plotly line graphs,
a results table breaking down frequency counts, percentages, and 
expected results (to run the Benford's test).

Addtionally, there are 3 tests to inform the user if the
data matches the expected distribution.

**⚠️ NOTE**: 
I do not think  the KS and Kupier's formulas are correct, and I have not dealt
with this many stats in years.
My goal was to implement them but I've been tweaking them for quite a while so I
wanted to send what I had, though I can say that these are not my strength.

## View Data
Once either the `/view/jobs` or `/view/data` pages return over 1000 results,
there is some rudimentary pagination by offset in place. You can paginate with the arrows,
or update the request parameter.

---
# Project Structure/Architecture Details
## Components
### Docker
 This project uses networked Docker containers and volumes for storing data.
### Flask
[Flask](https://flask.readthedocs.io/en/1.1.x/) is a Python-based, lightweight
Web Server Gateway Interface web application framework. Flask depends on a few
other Pallets projects that together, handles web pages,
web forms, routing requests, etc.

### Database Management and SQL operations
#### SQLAlchemy
The database and SQL operations are managed with [SQLAlchemy](https://docs.sqlalchemy.org).
SQLAlchemy is a library that consists of an SQL toolkit and an ORM.

#### PostgreSQL
The database (stored in a Docker volume) is PostgreSQL.
One of the containers is running pgAdmin to enable better
database maintenance, viewing, management, etc.

### Front-End
#### Jinja
The pages are rendered with [Jinja](https://palletsprojects.com/p/jinja/).
Jinja uses the curly-brace annotation to serve data dynamically.  You will find this data in the templates folder.
the render_template functions (see below) are seen mostly in run.py.
```html
<!-- my template file-->
<h1>Welcome! <small>My message to you: {{ page_data.hello_world }}</small></h1>
```
### Other front-end stuff: CSS/Javascript
This is currently using Bootstrap 5 and Fontawesome with other ancillary JavaScript libraries.
It also uses Plotly to render graphs.

## Project Structure
```
📁 parent_folder
  .gitignore -- unused, but nice to have for github
  README.md
  tracebacks.md
  widgets.md
  📁 app
    __init__.py
    run.py
    docker-compose.yml
    Dockerfile
    📁 config
    📁 data_access
    📁 env
    📁 models
    📁 services
    📁 static
    📁 templates
    📁 tests
    📁 util
```

### app/run.py
Found in the main app folder, the `run.py` file contains 
the things that are closest to the front-end, essentially.
The delineated allowable URLs (routes) are defined here, as well as
any custom Jinja template functions.
This is also where the app itself is created and app-specific
configurations are configured.

### app/config
This houses a few, small functions for verifying the required
database config variables have been provided in the env file and a 
dict with a mostly hard-coded logging config to set the format for the output, 
optional output file, etc.

### app/data_acccess
`data_acces/db_dto` contains a handful of functions for interacting with
the database. These are called by methods in `run.py`

### app/models
This contains some SQLAlchemy mixins (utility functions to allow for
easier introspection, validation, etc.) and model definitions for the 
tables in the database. 
If you need to update the table definitions, add new tables, this is where
you do it.

### app/services
This contains most of the functionality of the app like interacting
directly with the database, calculating the Benford's values, differences, etc.,
reading input files, and creating Plotly graphs to visualize the output.

### app/static
Basic webpage stuff like images, js, css libraries, etc.

### app/templates
Jinja templates for main views along with partials (specific snippets to 
render things like a table, a header, etc.).

### app/tests
Simple unit tests based on some of the services.

### app/util
Small library with functions that, in theory, could be more widely-used
across the app, though there are only a few in `common.py`.


