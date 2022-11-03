#!/bin/bash 

nuitka3 src/main.py --onefile --standalone --linux-icon=./JMC-icon.ico --remove-output --output-dir=./dist
cd dist
if [ -f JMC.bin ]; then
   rm JMC.bin
fi
mv main.bin JMC.bin
cd ..