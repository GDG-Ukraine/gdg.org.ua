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
    local config_file='environ'

    # Get variables
    local hostname=`_get_user_input 'Enter hostname (start with http:// or https://)' 'http://localhost:8080'`
    local db_url=`_get_user_input 'Enter database connection dsn string' 'mysql+mysqlconnector://mysql:mysql@localhost:3307/gdg'`
    local google_client_id=`_get_user_input 'Your Google client id' '<REPLACE_THIS>.apps.googleusercontent.com'`
    local google_client_secret=`_get_user_input 'Your Google client secret' '<REPLACE_THIS>'`

    # Combine all into config
    local config='{ "global": { "base_app_url": "'${hostname}'", "key":"sadsadsadasdsadasadsadsadasdsada", "google_oauth": { "id": "'${google_client_id}'", "secret": "'${google_client_secret}'" }, "alembic": {"sqlalchemy.url": "'${db_url}'"} }, "sqlalchemy_engine": { "url": "'${db_url}'" } }'


    echo "BASE_URL=$hostname" > "$config_file"
    echo "OAUTHLIB_INSECURE_TRANSPORT=1  # Change to zero if you use https" >> "$config_file"
    echo "DATABASE_URL=$db_url" >> "$config_file"
    echo "BLUEBERRYPY_CONFIG=$config" >> "$config_file"
}


_show_description
_main
echo "Done!"
