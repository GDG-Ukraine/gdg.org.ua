#! /usr/bin/env bash

BASEDIR=$(dirname "$0")

echo This is a temporary placeholder for the deploymet scenario
exit 0
openssl aes-256-cbc -K "$encrypted_237af1bf8448_key" -iv "$encrypted_237af1bf8448_iv" -in "$BASEDIR/deploy_key.enc" -out "$BASEDIR/deploy_key" -d
