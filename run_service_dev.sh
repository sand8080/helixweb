#!/bin/bash

BASENAME=`basename $0`
CUR_DIR=`dirname $0`
VENV_DIR=`readlink -f $CUR_DIR/.env`
echo $VENV_DIR
PYTHON_CMD="$VENV_DIR/bin/python"

pushd "$CUR_DIR"
export PYTHONPATH="$CUR_DIR/src:$CUR_DIR/../helixcore/src"
#DJANGO_CMD="$PYTHON_CMD $CUR_DIR/src/helixweb/manage.py runserver --settings=helixweb.settings_dev"
DJANGO_CMD="$PYTHON_CMD $CUR_DIR/src/helixweb/manage.py runserver 0.0.0.0:8000 --settings=helixweb.settings_dev"
echo $DJANGO_CMD
$DJANGO_CMD
popd
