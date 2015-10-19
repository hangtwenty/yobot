#!/usr/bin/env bash

# TODO(hangtwenty) refactor for less hardcoding

set -e

if [ -z ${VIRTUAL_ENV+x} ]; then
    echo "Please activate your virtualenv and then run this script."
    exit 127
fi

# TODO(hangtwenty) update w/ bashism to get absolute path to this script so this cd always works
# and can always CD back into this exact dir
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_DIR="$DIR/.."

rm -i /tmp/yobot-lambda.zip || true

pip install -r $PROJECT_DIR/requirements.txt

# copy all python files from the yobot directory. (recursive)
cd $PROJECT_DIR/yobot/
zip -r /tmp/yobot-lambda.zip .
echo "[.] Copied all Python from this directory into zipfile."

# as recommended here ...
# http://docs.aws.amazon.com/lambda/latest/dg/lambda-python-how-to-create-deployment-package.html
cd $VIRTUAL_ENV/lib/python2.7/site-packages/
zip -ur /tmp/yobot-lambda.zip *
echo "[.] Copied everything from virtualenv into zipfile."
cd $PROJECT_DIR

aws lambda update-function-code --function-name yobot --zip fileb:///tmp/yobot-lambda.zip
