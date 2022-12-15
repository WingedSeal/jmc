cd src/dist
del jmcfunction* /a
cd ..
python setup.py sdist bdist_wheel 
START /B /wait cmd /c "twine upload dist/jmcfunction*"
rmdir /s jmcfunction.egg-info
rmdir /s build
cd ..