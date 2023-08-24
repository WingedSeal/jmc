cd ./src/dist
rm -r jmcfunction* /a
cd ..
python setup.py sdist bdist_wheel 
twine upload dist/jmcfunction*
rm -r jmcfunction.egg-info
rm -r build
cd ..