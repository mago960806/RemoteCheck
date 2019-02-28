@echo off
del .\RemoteCheck.exe
pyinstaller.exe --distpath=.\ -F RemoteCheck.py -i icon.ico
rd /S /Q .\build
rd /S /Q .\__pycache__
del .\RemoteCheck.spec