web: blueberrypy serve --bind="0.0.0.0:$PORT" --environment="$ENV"
migrate-db: alembic -c config/alembic.ini -x environment="$ENV" upgrade head
apply-dev-fixtures: load_gdg_fixtures --env dev src/GDGUkraine/fixtures/fixtures.yaml
