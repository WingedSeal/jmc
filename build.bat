START /B /wait cmd /c "nuitka src/jmc/__main__.py --onefile --standalone --windows-icon-from-ico=./JMC-icon.ico --remove-output --output-dir=./dist --mingw64"
cd dist
del "JMC.exe"
ren "__main__.exe" "JMC.exe"
cd ..