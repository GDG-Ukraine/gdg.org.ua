#!/bin/sh
PENV=".env"
PENV_BIN_PATH=$PENV"/bin/"
PINST=$PENV_BIN_PATH"pip install --no-use-wheel -U -r"
WSGI=$PENV_BIN_PATH"gunicorn"
REQ_DIR="requirements"
OPEN_URL="xdg-open"
MIGRATOR=$PENV_BIN_PATH"alembic -c config/alembic.ini"
BWR="./node_modules/bower/bin/bower"
NPM="npm"
PRECOMMIT=$PENV_BIN_PATH"pre-commit"
BLUEBERRY=$PENV_BIN_PATH"blueberrypy serve -b"
TOX=$PENV_BIN_PATH"tox"
NOSE=$PENV_BIN_PATH"nosetests"

PID_PATH="/var/tmp/run"
STAGING_PORT="11010"

PROD_IF="127.0.0.1"
PROD_PORT="10110"
PROD_PID=$PID_PATH"/gdg.org.ua.pid"

DEV_IF="0.0.0.0"
DEV_PORT="8080"
DEV_PID=$PID_PATH"/gdg.org.ua.development.pid"

DEFAULT_EXPORTS="export BLUEBERRYPY_CONFIG='{ \"global\": { \"key\":\"<32-byte-str-for-aes>\", \"google_oauth\": { \"id\": \"<google_app_id>\", \"secret\": \"<google_app_secret>\" }, \"alembic\": {\"sqlalchemy.url\": \"mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock\"} }, \"sqlalchemy_engine\": { \"url\": \"mysql+mysqlconnector://<username>:<userpassword>@/<dbname>?unix_socket=/var/run/mysqld/mysqld.sock\" } }'"

deps (){ activate_env "$@"; front_deps "$@";
   $PINST $REQ_DIR/prod.txt
}

dev_deps (){ activate_env "$@"; front_deps "$@;"
   $PENV_BIN_PATH/pip install -U pip
   $PINST $REQ_DIR/dev.txt
   $PRECOMMIT install
}

test_deps (){ activate_env "$@"; front_deps "$@";
	$PINST $REQ_DIR/test.txt
}

test_env (){ activate_env "$@";
   $PINST $REQ_DIR/test-env.txt
}

front_deps () {
   $NPM install bower
   $BWR install
}

env (){
   case ${1} in
      "py35" )
         virtualenv --clear --prompt="[gdg.org.ua][py3.5] " -p python3.5 $PENV
         return 0;;
      "py34" )
         virtualenv --clear --prompt="[gdg.org.ua][py3.4] " -p python3.4 $PENV
         return 0;;
      * )
      while true; do
          read -p "Select python which you want to use:
1) Python 3.5
2) Python 3.4
Type one of selected: " sel
         case $sel in
            1* )
               virtualenv --clear --prompt="[gdg.org.ua][py3.5] " -p python3.5 $PENV
               break;;
            2* )
               virtualenv --clear --prompt="[gdg.org.ua][py3.4] " -p python3.4 $PENV
               break;;
          esac
      done;;
   esac
}

exports (){
   echo DEFAULT_EXPORTS > .exports
}

activate_env (){
   if [ ! -d $PENV ]; then env "$2"; fi
   . $PENV/bin/activate
   if [ ! -f .exports ]; then exports; fi
   . ./.exports
}

mkpidpath (){
   echo "Create PID directory: $(PID_PATH)"
   mkdir -p $PID_PATH 2>&1 >/dev/null
}

db (){ activate_env "$@";
   $MIGRATOR -x environment=dev upgrade head
}

prod_db (){ activate_env "$@";
   $MIGRATOR -x environment=prod upgrade head
}

migration (){ activate_env "$@";
   # WTF $COMMIT_MSG???!!
   $MIGRATOR -x environment=dev revision --autogenerate -m $COMMIT_MSG
   git add src/db/versions
   git commit -m $COMMIT_MSG
}

tests (){ test_nose "$@"; test_style "$@";
   python --version
}

test_envs (){ test_env "$@"; activate_env "$@";
   BLUEBERRYPY_CONFIG='{}' $TOX $TOX_ARGS
}

test_nose (){
   BLUEBERRYPY_CONFIG='{}' NOSE_TESTCONFIG_AUTOLOAD_YAML=config/test/app.yml $NOSE -w src/tests --tests=test_utils
}

test_style (){ test_deps "$@";
   BLUEBERRYPY_CONFIG='{}' $PRECOMMIT run --all-files
}

run_dev (){ activate_env "$@";
   $BLUEBERRY $DEV_IF:$DEV_PORT -P $DEV_PID
}

dev (){ dev_deps "$@"; run_dev "$@";
}

run (){ deps "$@"; db "$@"; run_prod "$@";
   $BLUEBERRY $PROD_IF:$PROD_PORT -P $PROD_PID -e production -d
}

run_prod (){ activate_env "$@";
   $BLUEBERRY $PROD_IF:$PROD_PORT -P $PROD_PID -e production -d
}

prod (){ deps "$@"; db "$@"; run_prod "$@";
}

restart_prod (){
   kill -SIGHUP `cat $PROD_PID`
}

reload_prod (){
   kill -SIGUSR1 `cat $PROD_PID`
}

stop_prod (){
   kill -SIGTERM `cat $PROD_PID`
}

case ${1} in
   "deps")           deps "$@";;
   "dev-deps")       dev_deps "$@";;
   "test-deps")      test_deps "$@";;
   "test-env")       test_env "$@";;
   "front-deps")     front_deps "$@";;
   "mkpidpath")      mkpidpath "$@";;
   "db")             db "$@";;
   "prod-db")        prod_db "$@";;
   "migration")      migration "$@";;
   "test")           tests "$@";;
   "test-envs")      test_envs "$@";;
   "test-nose")      test_nose "$@";;
   "test-style")     test_style "$@";;
   "run-dev")        run_dev "$@";;
   "dev")            dev "$@";;
   "run")            run "$@";;
   "run-prod")       run_prod "$@";;
   "prod")           prod "$@";;
   "restart-prod")   restart_prod "$@";;
   "reload-prod")    reload_prod "$@";;
   "stop-prod")      stop_prod "$@";;
   *)                deps "$@";;
esac
