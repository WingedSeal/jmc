#!/bin/bash 

nuitka3 src/run.py --onefile --standalone --linux-icon=./JMC-icon.ico --remove-output --output-dir=./dist
cd dist
if [ -f JMC.bin ]; then
   rm JMC.bin
fi
mv run.bin JMC.bin
cd ..