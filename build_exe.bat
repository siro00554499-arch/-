@echo off
echo Installing requirements...
pip install pygame pyinstaller

echo Building EXE...
pyinstaller --noconsole --onefile --icon=tetorisu.ico --name="TetrisUnofficial" --strip --exclude-module tkinter --exclude-module unittest --exclude-module email --exclude-module xml --exclude-module pydoc main.py

echo Cleaning up...
rmdir /s /q build
del /q TetrisUnofficial.spec
move /y dist\TetrisUnofficial.exe .
rmdir /s /q dist

echo Build complete!
pause
