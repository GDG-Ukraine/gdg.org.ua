#! /usr/bin/env bash

BASEDIR=$(dirname "$0")
DEPLOYMENT_KEY="$BASEDIR/deploy_key"

function clean_up {
    # Perform program exit housekeeping
    echo Cleanning up stuff
    rm -f "$DEPLOYMENT_KEY"
    exit
}

trap clean_up SIGHUP SIGINT SIGTERM

echo Decrypting a deployment key...
openssl aes-256-cbc -K "$encrypted_237af1bf8448_key" -iv "$encrypted_237af1bf8448_iv" -in "${DEPLOYMENT_KEY}.enc" -out "$DEPLOYMENT_KEY" -d
chmod 600 "$DEPLOYMENT_KEY"

echo Adding a deployment repo remote...
git remote add dokku dokku@linode.mrgall.com:gdg.org.ua

echo Pushing the app to production...
# Ref: http://stackoverflow.com/a/41612988/595220
#GIT_SSH_COMMAND="ssh -i $DEPLOYMENT_KEY -F /dev/null" git push dokku master
GIT_SSH_COMMAND="ssh -i $DEPLOYMENT_KEY" git push dokku master

clean_up
