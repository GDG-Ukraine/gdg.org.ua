# gdg.org.ua
This is the event registration system for GDG Ukraine events.

Tasks: [![Stories in Ready](https://badge.waffle.io/GDG-Ukraine/gdg.org.ua.svg?label=Stage:%20Ready%20For%20Dev&title=Ready%20for%20dev)](http://waffle.io/GDG-Ukraine/gdg.org.ua)

CI:
master: [![`master` brach status](https://api.travis-ci.org/GDG-Ukraine/gdg.org.ua.svg?branch=master)](https://travis-ci.org/GDG-Ukraine/gdg.org.ua)
api-for-admin: [![`api-for-admin` brach status](https://api.travis-ci.org/GDG-Ukraine/gdg.org.ua.svg?branch=api-for-admin)](https://travis-ci.org/GDG-Ukraine/gdg.org.ua/branches)

## Requirements:

    Python 3.5.0 (it is recommended to use pyenv for dev environment)
    NodeJS 5.0.0 (it is recommended to use nvm for dev environment)
    MySQL        (MariaDB works well)

## Prerequisites:

    $ cd gdg.org.ua

### Create `.exports` file with following contents:
    export BLUEBERRYPY_CONFIG='{ "global": { "key":"<32-byte-str-for-aes>", "google_oauth": { "id": "<google_app_id>", "secret": "<google_app_secret>" }, "alembic": {"sqlalchemy.url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock"} }, "sqlalchemy_engine": { "url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock" } }'

### For dev add following line as well:
    export OAUTHLIB_INSECURE_TRANSPORT=1

## How to run it on localhost

* First, prepare the environment:

    $ make env

    $ make dev-deps

* Create database tables:

    [gdg.org.ua]$ make db

* Start application:

    [gdg.org.ua]$ make run-dev

* Open `http://localhost:8080/` in your favourite browser and have fun :)

P.S. `make dev` combines steps above except db target

## How to run it in production

* Prepare the environment:

    $ make env
    [gdg.org.ua]$ make deps

* Create database tables:

    [gdg.org.ua]$ make prod-db

* Start application:

    [gdg.org.ua]$ make run-prod

## How to upgrade production

We have `bin/update_gdg` script for this

## Running tests

    [gdg.org.ua]$ make test

You can use [`tox`](https://tox.readthedocs.org) to run tests as well. Unfortunately, due to some bug in tox itself some special steps are required.

    [gdg.org.ua]$ make test-envs

You can also run only specific set of tests. To do that, add `-e toxenv[,toxenv]` to tox comand. For example, to run tests only for python3.5, use the following command:

    [gdg.org.ua]$ make TOX_ARGS="-e py35-codestyle,py35-nosetests" test-envs

## Troubleshooting

### Converting packages to python3
You may need to use 2to3 utility to convert 2nd python version code into py3k, i.e.:

    $ 2to3 -w path/to/gdg.org.ua/env/lib/python*/site-packages/package

### Errors with installing mysq-connector-python
If you are getting errors about pip cannot find `mysql-connector-python` you can use the following workaround:

    [gdg.org.ua]$ pip install http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.0.4.zip#md5=3df394d89300db95163f17c843ef49df

or download the `mysql-connector-python` archive manually and then try to install requirements again.

If you see any wheel-related error output, you may want to avoid it by using
`--no-use-wheel` option. E.g.:

    [gdg.org.ua]$ pip install coverage --no-use-wheel
