cd src
python setup.py sdist bdist_wheel 
twine upload dist/jmcfunction*
cd ..