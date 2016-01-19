# gdg.org.ua
This is the event registration system for GDG Ukraine events.

Tasks: [![Stories in Ready](https://badge.waffle.io/GDG-Ukraine/gdg.org.ua.svg?label=ready-for-dev&title=Ready%20for%20dev)](http://waffle.io/GDG-Ukraine/gdg.org.ua)

## Requirements:

    Python 3.5
    MySQL db

## How to run it on localhost

* First, prepare the environment:

        $ cd gdg.org.ua
        $ virtualenv --clear --prompt="[gdg.org.ua]" -p python3.5 env
        $ . env/bin/activate
        [gdg.org.ua]$ pip install -r dev.txt
        [gdg.org.ua]$ pip install -e .

* Set up config in environment variables:

        [gdg.org.ua]$ export BLUEBERRYPY_CONFIG='{ "global": { "key":"<32-byte-str-for-aes>", "google_oauth": { "id": "<google_app_id>", "secret": "<google_app_secret>" }, "alembic": {"sqlalchemy.url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock"} }, "sqlalchemy_engine": { "url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock" } }'
        [gdg.org.ua]$ export OAUTHLIB_INSECURE_TRANSPORT=1

* Create database tables:

        [gdg.org.ua]$ alembic -c config/alembic.ini upgrade head

* Start application:

        [gdg.org.ua]$ blueberrypy serve -b 0.0.0.0:8080

* Open `http://localhost:8080/` in your favourite browser and have fun :)

Finally, to log out from virtualenv you may simply type:

    [gdg.org.ua]$ deactivate

## How to run it in production

* Prepare the environment:

        $ cd gdg.org.ua
        $ virtualenv --clear --prompt="[gdg.org.ua]" -p python3.5 env
        $ . env/bin/activate
        [gdg.org.ua]$ pip install -r requirements.txt
        [gdg.org.ua]$ pip install -e .

* Set up config in environment variables:

        [gdg.org.ua]$ export BLUEBERRYPY_CONFIG='{ "global": { "key":"<32-byte-str-for-aes>", "google_oauth": { "id": "<google_app_id>", "secret": "<google_app_secret>" }, "alembic": {"sqlalchemy.url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock"} }, "sqlalchemy_engine": { "url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock" } }'

* If you don't have HTTPS enabled you'll need to set this variable as well:

        [gdg.org.ua]$ export OAUTHLIB_INSECURE_TRANSPORT=1

* Create database tables:

        [gdg.org.ua]$ alembic -c config/alembic.ini -x environment=prod upgrade head

* Start application:

        [gdg.org.ua]$ ./init_production.sh start

## How to upgrade production

We have `bin/update_gdg` script for this

## Troubleshooting

### Converting packages to python3
You may need to use 2to3 utility to convert 2nd python version code into py3k, i.e.:

    $ 2to3 -w path/to/gdg.org.ua/env/lib/python*/site-packages/package

### Errors with installing mysq-connector-python
If you are getting errors about pip cannot find `mysql-connector-python` you can use the following workaround:

    [gdg.org.ua]$ pip install http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.0.4.zip#md5=3df394d89300db95163f17c843ef49df

or download the `mysql-connector-python` archive manually and then try to install requirements again.
