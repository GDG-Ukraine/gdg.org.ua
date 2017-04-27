.. image:: https://badge.waffle.io/GDG-Ukraine/gdg.org.ua.svg?label=Stage: Ready For Dev&title=Ready for dev
   :target: http://waffle.io/GDG-Ukraine/gdg.org.ua
   :alt: Stories in Ready

.. image:: https://api.travis-ci.org/GDG-Ukraine/gdg.org.ua.svg?branch=master
   :target: https://travis-ci.org/GDG-Ukraine/gdg.org.ua
   :alt: `master` branch status

.. image:: https://codecov.io/gh/GDG-Ukraine/gdg.org.ua/branch/master/graph/badge.svg
   :target: https://codecov.io/gh/GDG-Ukraine/gdg.org.ua
   :alt: codecov

gdg.org.ua
==========
This is the event registration system for GDG Ukraine events.


Requirements:
-------------

* Python 3.5+  (it is recommended to use pyenv for dev environment)
* NodeJS 5.0+  (it is recommended to use nvm for dev environment)
* MySQL        (MariaDB works well)

Prerequisites:
--------------

.. code:: shell
   :number-lines:

    $ cd gdg.org.ua

Create DB and user, with smth like:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~


.. code:: shell
   :number-lines:

    $ mysql -uroot -e "CREATE DATABASE <dbname>; GRANT ALL PRIVILEGES ON <dbname>.* TO <username>@'localhost' IDENTIFIED BY '<userpassword>'; FLUSH HOSTS; FLUSH PRIVILEGES;"

Create `.exports` file with following contents:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell
   :number-lines:

    export BLUEBERRYPY_CONFIG='{ "global": { "key":"<32-byte-str-for-aes>", "google_oauth": { "id": "<google_app_id>", "secret": "<google_app_secret>" }, "alembic": {"sqlalchemy.url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock"} }, "sqlalchemy_engine": { "url": "mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock" } }'

For dev add following line as well:
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code:: shell
   :number-lines:

    export OAUTHLIB_INSECURE_TRANSPORT=1

How to run it on localhost
--------------------------

* First, prepare the environment:

.. code:: shell
   :number-lines:

    $ make env
    $ make dev-deps

* Create database tables:

.. code:: shell
   :number-lines:

    $ make db

* Start application:

.. code:: shell
   :number-lines:

    $ make run-dev

* Open `http://localhost:8080/` in your favourite browser and have fun :)

P.S. `make dev` (or just `make`) combines steps above except db target

How to run it in production
---------------------------

* Prepare the environment:

.. code:: shell
   :number-lines:

    $ make env
    $ make deps

* Create database tables:

.. code:: shell
   :number-lines:

    $ make prod-db

* Start application:

.. code:: shell
   :number-lines:

    $ make run-prod

How to upgrade production (DEPRECATED!)
---------------------------------------

We have ``bin/update_gdg`` script for this

Running tests
-------------

.. code:: shell
   :number-lines:

    $ make test

You can use [`tox`](https://tox.readthedocs.org) to run tests as well. Unfortunately, due to some bug in tox itself some special steps are required.

.. code:: shell
   :number-lines:

    $ make test-envs

Enabling env
------------
If you for some reason need to run shell with env activated, run this:

.. code:: shell
   :number-lines:

    $ make activate-env
    [gdg.org.ua][py3.5] $ _

Troubleshooting
---------------

Errors with installing mysql-connector-python
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
If you are getting errors about pip cannot find `mysql-connector-python` you can use the following workaround:

.. code:: shell
   :number-lines:

    $ make activate-env
    [gdg.org.ua][py3.5] $ pip install http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.0.4.zip#md5=3df394d89300db95163f17c843ef49df

or download the `mysql-connector-python` archive manually and then try to install requirements again.

If you see any wheel-related error output, you may want to avoid it by using
`--no-use-wheel` option. E.g.:

.. code:: shell
   :number-lines:

    $ make activate-env
    [gdg.org.ua][py3.5] $ pip install coverage --no-use-wheel
