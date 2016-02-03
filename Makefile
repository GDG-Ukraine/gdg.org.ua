PINST=pip install --no-use-wheel -U -r
WSGI=gunicorn
REQ_DIR=requirements
READ=more
ISSUES_URL=https://github.com/GDG-Ukraine/gdg.org.ua/issues
OPEN_URL=xdg-open
MIGRATOR=alembic -c config/alembic.ini
BWR=bower
BLUEBERRY=blueberrypy serve -b
PENV=env

PID_PATH=/var/tmp/run
STAGING_PORT=11010

PROD_IF=127.0.0.1
PROD_PORT=10110
PROD_PID=$(PID_PATH)/gdg.org.ua.pid

DEV_IF=0.0.0.0
DEV_PORT=8080
DEV_PID=$(PID_PATH)/gdg.org.ua.development.pid

all: dev

deps: env front-deps
	$(PINST) $(REQ_DIR)/prod.txt

dev-deps: env front-deps
	$(PINST) $(REQ_DIR)/dev.txt

test-deps: env front-deps
	$(PINST) $(REQ_DIR)/test.txt

test-env:
	$(PINST) $(REQ_DIR)/test-env.txt

front-deps:
	$(BWR) install

mkenv:
	virtualenv --clear --prompt="[gdg.org.ua][py3.5] " -p python3.5 $(PENV)

env: mkpidpath
	. $(PENV)/bin/activate
	if test -f .exports; then . .exports; fi

mkpidpath:
	echo "Create PID directory: $(PID_PATH)"
	mkdir -p "$(PID_PATH)" 2>&1 >/dev/null

readme:
	$(READ) README.md

issues:
	echo "Please check out issues at $(ISSUES_URL)"

issue:
	$(OPEN_URL) "$(ISSUES_URL)/$1"

help: readme issues
	$(OPEN_URL) "$(ISSUES_URL)"

db: env
	$(MIGRATOR) -x environment=dev upgrade head

migration: env
	$(MIGRATOR) -x environment=dev revision --autogenerate -m "$1"
	git add src/db/versions
	git commit -m "$1"

test: test-nose test-style
	python --version

test-envs: test-env
	BLUEBERRYPY_CONFIG='{}' tox $(TOX_ARGS)

test-nose: test-deps
	BLUEBERRYPY_CONFIG='{}' NOSE_TESTCONFIG_AUTOLOAD_YAML=config/test/app.yml nosetests -w src/tests --tests=test_utils

test-style: test-deps
	BLUEBERRYPY_CONFIG='{}' pre-commit run --all-files

run-dev: env
	$(BLUEBERRY) $(DEV_IF):$(DEV_PORT) -P $(DEV_PID)

dev: dev-deps run-dev

run: deps db env
	echo "This is not implemented yet!" || $(WSGI) not_implemented.wsgi $1

run-prod: env
	$(BLUEBERRY) $(PROD_IF):$(PROD_PORT) -P $(PROD_PID) -e production -d

prod: deps db run-prod

restart-prod:
	kill -SIGHUP `cat $PROD_PID`

reload-prod:
	kill -SIGUSR1 `cat $PROD_PID`

stop-prod:
	kill -SIGTERM `cat $PROD_PID`
