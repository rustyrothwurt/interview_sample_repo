# Official Python runtime as a parent image
FROM python:3.8

# this argument comes from docker-compose.yml or as a build-arg
# appending to docker build (--build-arg flask_env=development)
ARG FLASK_RUN_HOST
ARG FLASK_RUN_PORT
ARG CONFIG_FILE

# Set the working directory to /app and copy the contents into app
WORKDIR /app
ADD .. /app

# Install any needed packages
# TODO: future task item - put back into requirements.txt
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install regex
RUN pip install requests
RUN pip install pandas
RUN pip install psycopg2-binary
RUN pip install SQLAlchemy
RUN pip install plotly==5.4.0

# these are likely redundant but were placed here
# to fix a bug...
# but the bug was in another place
ENV FLASK_RUN_HOST=$FLASK_RUN_HOST
RUN export FLASK_RUN_HOST=$FLASK_RUN_HOST
ENV FLASK_RUN_PORT=$FLASK_RUN_PORT
RUN export FLASK_RUN_PORT=$FLASK_RUN_PORT
ENV ENV_FILE_PATH=$CONFIG_FILE
#RUN it
CMD ["python", "run.py"]
