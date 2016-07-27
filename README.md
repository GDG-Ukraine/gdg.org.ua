# gdg.org.ua
This is the event registration system for GDG Ukraine events.

[![Stories in Ready](https://badge.waffle.io/GDG-Ukraine/gdg.org.ua.svg?label=Stage: Ready For Dev&title=Ready for dev)](http://waffle.io/GDG-Ukraine/gdg.org.ua)

[![`master` branch status](https://api.travis-ci.org/GDG-Ukraine/gdg.org.ua.svg?branch=master)](https://travis-ci.org/GDG-Ukraine/gdg.org.ua) [![codecov](https://codecov.io/gh/GDG-Ukraine/gdg.org.ua/branch/master/graph/badge.svg)](https://codecov.io/gh/GDG-Ukraine/gdg.org.ua) [![Requirements Status](https://requires.io/github/GDG-Ukraine/gdg.org.ua/requirements.svg?branch=master)](https://requires.io/github/GDG-Ukraine/gdg.org.ua/requirements/?branch=master)

## Requirements:

    Python 3.5.0 (it is recommended to use pyenv for dev environment)
    NodeJS 5.0.0 (it is recommended to use nvm for dev environment)
    MySQL        (MariaDB works well)
    Mercurial    (because there's some `hg+` dependencies)

## Prerequisites:

    $ cd gdg.org.ua

### Create DB and user, with smth like:

    $ mysql -uroot -e "CREATE DATABASE <dbname>; GRANT ALL PRIVILEGES ON <dbname>.* TO <username>@'localhost' IDENTIFIED BY '<userpassword>'; FLUSH HOSTS; FLUSH PRIVILEGES;"

### Create `.exports` file with following contents:
    export BLUEBERRYPY_CONFIG='{ "global": { "key":"<32-byte-str-for-aes>", "google_oauth": { "id": "<google_app_id>", "secret": "<google_app_secret>" }, "alembic": {"sqlalchemy.url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock"} }, "sqlalchemy_engine": { "url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock" } }'

### For dev add following line as well:
    export OAUTHLIB_INSECURE_TRANSPORT=1

## How to run it on localhost

* First, prepare the environment:

```
    $ make env
    $ make dev-deps
```

* Create database tables:

```
    $ make db
```

* Start application:

```
    $ make run-dev
```

* Open `http://localhost:8080/` in your favourite browser and have fun :)

P.S. `make dev` (or just `make`) combines steps above except db target

## How to run it in production

* Prepare the environment:

```
    $ make env
    $ make deps
```

* Create database tables:

```
    $ make prod-db
```

* Start application:

```
    $ make run-prod
```

## How to upgrade production

We have `bin/update_gdg` script for this

## Running tests

    $ make test

You can use [`tox`](https://tox.readthedocs.org) to run tests as well. Unfortunately, due to some bug in tox itself some special steps are required.

    $ make test-envs

You can also run only specific set of tests. To do that, add `-e toxenv[,toxenv]` to tox comand. For example, to run tests only for python3.5, use the following command:

    $ make TOX_ARGS="-e py35-codestyle,py35-nosetests" test-envs

## Enabling env
If you for some reason need to run shell with env activated, run this:

    $ make activate-env
    [gdg.org.ua][py3.5] $ _

## Troubleshooting

### Converting packages to python3
You may need to use 2to3 utility to convert 2nd python version code into py3k, i.e.:

    $ 2to3 -w path/to/gdg.org.ua/env/lib/python*/site-packages/package

### Errors with installing mysql-connector-python
If you are getting errors about pip cannot find `mysql-connector-python` you can use the following workaround:

    $ make activate-env
    [gdg.org.ua][py3.5] $ pip install http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.0.4.zip#md5=3df394d89300db95163f17c843ef49df

or download the `mysql-connector-python` archive manually and then try to install requirements again.

If you see any wheel-related error output, you may want to avoid it by using
`--no-use-wheel` option. E.g.:

    $ make activate-env
    [gdg.org.ua][py3.5] $ pip install coverage --no-use-wheel
