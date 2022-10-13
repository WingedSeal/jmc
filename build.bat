START /B /wait cmd /c "nuitka src/main.py --onefile --standalone --windows-icon-from-ico=./JMC-icon.ico --remove-output --output-dir=./dist --mingw64"
cd dist
del "JMC.exe"
ren "main.exe" "JMC.exe"
cd ..