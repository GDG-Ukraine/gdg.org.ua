PINST=pip install -r
WSGI=gunicorn
REQ_DIR=requirements
READ=more
ISSUES_URL=https://github.com/GDG-Ukraine/gdg.org.ua/issues
OPEN_URL=xdg-open
MIGRATOR=alembic -c config/dev/alembic.ini
BWR=bower
BLUEBERRY=blueberrypy

PROD_IF=127.0.0.1
PROD_PORT=10110
PROD_PID_PATH=/var/tmp/run
PROD_PID=$(PID_PATH)/gdg.org.ua.pid

DEV_IF=0.0.0.0
DEV_PORT=8080
DEV_PID_PATH=/var/tmp/run
DEV_PID=$(PID_PATH)/gdg.org.ua.development.pid

STAGING_PORT=11010


all: dev

deps: env front-deps
	$(PINST) $(REQ_DIR)/prod.txt

dev-deps: env front-deps
	$(PINST) $(REQ_DIR)/dev.txt

test-deps: env front-deps
	$(PINST) $(REQ_DIR)/test.txt

front-deps:
	$(BWR) install

mkenv:
	virtualenv --clear --prompt="[gdg.org.ua][py3.5] " -p python3.5 .env

env:
	. .env/bin/activate
	. ~/.exports &2>1 >/dev/null
	mkdir -p $PID_PATH &2>1 >/dev/null

readme:
	$(READ) README.md

issues:
	echo "Please check out issues at $(ISSUES_URL)"

issue:
	OPEN_URL "$(ISSUES_URL)/$1"

help: readme issues
	OPEN_URL "$(ISSUES_URL)"

db: env
	$(MIGRATOR) -x environment=dev upgrade head

migration: env
	$(MIGRATOR) -x environment=dev revision --autogenerate -m "$1"
	git add src/db/versions
	git commit -m "$1"

test: test-deps env
	tox

dev: dev-deps env
	$(BLUEBERRY) -b $DEV_IF:$DEV_PORT -P $DEV_PID

run: deps db env
	echo "This is not implemented yet!" || $(WSGI) not_implemented.wsgi $1

run-prod: deps db env
	$(BLUEBERRY) -b $PROD_IF:$PROD_PORT -P $PROD_PID -e production -d

restart-prod:
	kill -SIGHUP `cat $PROD_PID`

reload-prod:
	kill -SIGUSR1 `cat $PROD_PID`

stop-prod:
	kill -SIGTERM `cat $PROD_PID`
