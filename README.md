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
```
    $ cd gdg.org.ua
```
### For dev add following line as well:
```
    export OAUTHLIB_INSECURE_TRANSPORT=1
```
## How to run it on localhost
*Note: if the make.sh is not executable, you should call `chmod +x make.sh`*

#### Command by command instruction

* First, prepare the environment:
```
    $ ./make.sh dev-deps
```
* While dependencies are installing, update the placeholder values in .exports file (use preffered text editor: vim, nano, atom, etc.)

* Create database tables:
```
    $ ./make.sh db
```
* Start application:
```
    $ ./make.sh run-dev
```
* Open `http://localhost:8080/` in your favourite browser and have fun :)

#### When the environment is already set up and .exports file has no placeholders, you can call this
```
    $ ./make.sh dev
```

## How to run it in production

* Prepare the environment:
```
    $ ./make.sh deps
```
* Create database tables:
```
    $ ./make.sh prod-db
```
* Start application:
```
    $ ./make.sh run-prod
```
## How to upgrade production

We have `bin/update_gdg` script for this

## Running tests
```
    $ ./make.sh test
```
#### Tox testing

You can use [`tox`](https://tox.readthedocs.org) to run tests as well. Unfortunately, due to some bug in tox itself some special steps are required.
```
    $ ./make.sh test-envs
```
You can also run only specific set of tests. To do that, add `-e toxenv[,toxenv]` to tox comand. For example, to run tests only for python3.5, use the following command:
```
    $ ./make.sh test-envs TOX_ARGS="-e py35-codestyle,py35-nosetests"
```
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
