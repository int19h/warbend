@echo off
setlocal

call "%~dp0\env.cmd"
if errorlevel 1 goto :eof

cd "%USERPROFILE%\Documents\Mount&Blade Warband Savegames\Native"
%PYTHON% -i -c "execfile(r'%~dp0interactive.py')"
