gdg.org.ua
==========

Database of GDG members' contacts, events and some 'kostyl's

# Requirements:

    >=Python 3.2 (not tested on older versions)
    >=virtualenv 1.8 (at least, otherwise you will not be able to set python 3.2 version as default into the env)

# How to run it on localhost

* First, prepair environment:

        $ cd gdg.org.ua
        $ virtualenv --clear --prompt="[gdg.org.ua] (py3k)
        " -p python3.2 env
        $ source env/bin/activate
        $ vim config/dev/app.yml
            // enter db uri here. i.e. mysql+mysqlconnector://<username>:<userpassword>@<dbhost>[:<dbport>]/<dbname>
        $ pip install https://bitbucket.org/webknjaz/blueberrypy-wk
        $ pip install -e .
        $ blueberrypy -b 0.0.0.0:8080

* Open ```http://localhost:8080/``` in your favourite browser and have fun :)

Finally, to log out from virtualenv you may simply type:

        $ deactivate

# Trouble shooting

You may need to use 2to3 utility to convert 2nd python version code into py3k, i.e.:

        $ 2to3 -w path/to/gdg.org.ua/env/lib/python3.2/site-packages/package