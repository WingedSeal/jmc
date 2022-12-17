#!/bin/bash 

REGEX_VERSION="(?<=').*?(?=')"
# Fetch the 7th line of `__main__.py`, which contains the VERSION variable.
# TODO: don't rely on the fact that VERSION is the 7th line of code.
VERSION=$(sed '7!d' src/jmc/__main__.py)
# Apply regex to separate the contained value.
VERSION=$(echo "$VERSION" | grep -P "$REGEX_VERSION" -o)

nuitka3 src/run.py --onefile --standalone --linux-icon=./JMC-icon.ico --remove-output --output-dir=./dist
cd dist
if [ -f JMC.bin ]; then
   rm JMC.bin
fi
mv run.bin JMC-$VERSION.bin
cd ..
