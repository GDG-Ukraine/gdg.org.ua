# gdg.org.ua
This is the event registration system for GDG Ukraine events.

Tasks: [![Stories in Ready](https://badge.waffle.io/GDG-Ukraine/gdg.org.ua.svg?label=ready-for-dev&title=Ready%20for%20dev)](http://waffle.io/GDG-Ukraine/gdg.org.ua)

## Requirements:

    >=Python 3.2 (not tested on older versions)
    >=virtualenv 1.8 (at least, otherwise you will not be able to set python 3.2 version as default into the env)

## How to run it on localhost

* First, prepare the environment:

        $ cd gdg.org.ua
        $ virtualenv --clear --prompt="[gdg.org.ua]" -p python3.2 env
        $ source env/bin/activate
        [gdg.org.ua]$ vim config/dev/app.yml
            // enter db uri here. i.e. mysql+mysqlconnector://<username>:<userpassword>@<dbhost>[:<dbport>]/<dbname>
        [gdg.org.ua]$ pip install -r requirements.txt
        [gdg.org.ua]$ pip install -e .

* Create database tables (skip this step if you already have a database with all project tables):

        [gdg.org.ua]$ echo "locals()['create_all']()" | blueberrypy console

* Start application:

        [gdg.org.ua]$ blueberrypy serve -b 0.0.0.0:8080

* Open ```http://localhost:8080/``` in your favourite browser and have fun :)

Finally, to log out from virtualenv you may simply type:

    [gdg.org.ua]$ deactivate

## Troubleshooting

### Converting packages to python3
You may need to use 2to3 utility to convert 2nd python version code into py3k, i.e.:

    $ 2to3 -w path/to/gdg.org.ua/env/lib/python3.2/site-packages/package

### Errors with installing mysq-connector-python
If you are getting errors about pip cannot find `mysql-connector-python` you can use the following workaround:

    [gdg.org.ua]$ pip install http://cdn.mysql.com/Downloads/Connector-Python/mysql-connector-python-2.0.4.zip#md5=3df394d89300db95163f17c843ef49df

and then try to install requirements again.
