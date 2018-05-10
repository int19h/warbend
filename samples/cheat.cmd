@echo off
setlocal

call "%~dp0\env.cmd"
if errorlevel 1 goto :eof

:: Set these accordingly. Note that when dumping XML, the destination file name
:: has .xml appended at the end - so e.g. sg08.sav becomes sg08.sav.xml - but
:: still goes into the same folder as the .sav file would.
set "INPUT=%USERPROFILE%\Documents\Mount&Blade Warband Savegames\Native\sg00.sav"
set "OUTPUT=%USERPROFILE%\Documents\Mount&Blade Warband Savegames\Native\sg08.sav"
::set OUTPUT=output\sg00.sav

%PYTHON% "%~dp0\cheat.py" "%INPUT%" "%OUTPUT%"
:: >..\output\log.txt
