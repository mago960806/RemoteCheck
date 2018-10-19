@echo off
del .\RemoteCheck.exe
C:\ProgramData\Miniconda3\envs\ssh_login\Scripts\pyinstaller.exe --distpath=.\ -F RemoteCheck.py -i icon.ico
rd /S /Q .\build
rd /S /Q .\__pycache__
del .\RemoteCheck.spec