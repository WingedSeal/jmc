cd src/dist
del jmcfunction* /a
cd ..
python setup.py sdist bdist_wheel 
START /B /wait cmd /c "twine upload dist/jmcfunction*"
rmdir /s /Q jmcfunction.egg-info
rmdir /s /Q build
cd ..