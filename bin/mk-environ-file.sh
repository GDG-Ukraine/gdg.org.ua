#!/bin/bash


_show_description() {
    local description='
https://github.com/GDG-Ukraine/gdg.org.ua needs an environ file to store some sensitive configuration.

This will guide you through the process of environ file creation
    '
    echo "$description"
}

_get_user_input() {
    # Usage: _get_user_input PROMPT DEFAULT_VALUE
    prompt="$1"
    default_value="$2"

    echo "$prompt" > /dev/tty
    echo "default: $default_value" > /dev/tty
    read a_value
    if [ -z "$a_value" ]; then
        a_value="$default_value"
    fi
    echo "$a_value"
}


_main() {
    local config_file='.env'

    # Get variables
    local app_root=`_get_user_input 'Enter full path to your app root dir (use /work to run in vagga)' "$(pwd)"`
    local hostname=`_get_user_input 'Enter hostname (start with http:// or https://)' 'http://localhost:8080'`
    local db_url=`_get_user_input 'Enter database connection dsn string' 'mysql+mysqlconnector://mysql:mysql@localhost:3307/gdg'`
    local google_client_id=`_get_user_input 'Your Google client id' '<REPLACE_THIS>.apps.googleusercontent.com'`
    local google_client_secret=`_get_user_input 'Your Google client secret' '<REPLACE_THIS>'`

    local cache_dir="$app_root/.cache"
    local templates_dir="$app_root/src/GDGUkraine/templates"

    # Combine all into config
    local config='{ "global": { "CWD": "'${app_root}'", "base_app_url": "'${hostname}'", "key":"sadsadsadasdsadasadsadsadasdsada", "google_oauth": { "id": "'${google_client_id}'", "secret": "'${google_client_secret}'" }, "alembic": {"sqlalchemy.url": "'${db_url}'"} }, "sqlalchemy_engine": { "url": "'${db_url}'" }, "jinja2": { "bytecode_cache": { "!!python/object:jinja2.bccache.FileSystemBytecodeCache": {"directory": "'${cache_dir}'", "pattern": "__jinja2_%s.cache" } }, "loader": {"!!python/object:jinja2.loaders.FileSystemLoader": {"encoding": "utf-8", "searchpath": ["'${templates_dir}'"] } } } }'

    echo "APP_ROOT=$app_root" > "$config_file"
    echo "APP_PACKAGE=GDGUkraine" >> "$config_file"
    echo "BASE_URL=$hostname" >> "$config_file"
    # use insecure transport if basename is not https://
    case $hostname in
        https://* ) echo "Not setting OAUTHLIB_INSECURE_TRANSPORT as HTTPS is used" ;;
        * )  echo "OAUTHLIB_INSECURE_TRANSPORT=1" >> "$config_file" ;;
    esac

    echo "DATABASE_URL=$db_url" >> "$config_file"
    echo "BLUEBERRYPY_CONFIG=$config" >> "$config_file"
}


_show_description
_main
echo "Done!"
