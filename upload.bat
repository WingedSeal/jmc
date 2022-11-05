cd src/dist
del jmcfunction* /a
cd ..
python setup.py sdist bdist_wheel 
twine upload dist/jmcfunction*
rmdir /s jmcfunction.egg-info
rmdir /s build
cd ..