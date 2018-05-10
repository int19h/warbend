@echo off
setlocal

call "%~dp0\env.cmd"
if errorlevel 1 goto :eof

cd "%~dp0\..\output"
%PYTHON% -i -c "execfile(r'%~dp0interactive.py')"
