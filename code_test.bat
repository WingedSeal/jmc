@echo off
echo =====================================
echo ^> Code Cyclomatic Complexity (radon)
echo =====================================
radon cc src/jmc --min C -s --total-average
echo =====================================
echo ^> Code Maintainability Index (radon) 
echo =====================================
radon mi src/jmc --min B -s
echo ==================================
echo ^> Unit/Integration Tests (python)
echo ==================================
python src/tests/test_all.py || exit 1
echo ====================
echo ^> Type hints (mypy)
echo ====================
mypy ./src/jmc
echo =================================
echo ^> Code Style(PEP8) (pycodestyle)
echo =================================
pycodestyle ./src --ignore=E501,W50
@REM pylint src/jmc --disable=C0301,W1201,W1203,R0913
@REM pylint src/jmc --disable=C,W,R --enable=C0116  // Missing function docstring
@REM pylint src/jmc --disable=C,W,R --enable=W1309  // F-string that does not have any interpolated variables 