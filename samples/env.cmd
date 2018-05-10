@echo off

:: Uncomment the below statements, and set the value according to where Python
:: is installed on your system, to override automatic detection from registry.
set PYTHONDIR=C:\Python\PyPy-2.7\
set PYTHONEXE=pypy.exe
set PYTHONFLAGS=

:: set PYTHONDIR=C:\Program Files (x86)\IronPython 2.7\
:: set PYTHONEXE=ipy64.exe

:: If not set above, find it in registry. Look for 64-bit first.
if "%PYTHONDIR%" == "" (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Python\PythonCore\2.7\InstallPath"  2^>^&1^|find "REG_"') do set PYTHONDIR=%%b
)
:: If not found, look for 32-bit.
if "%PYTHONDIR%" == "" (
    for /f "tokens=2*" %%a in ('reg query "HKEY_LOCAL_MACHINE\SOFTWARE\WOW6432Node\Python\PythonCore\2.7\InstallPath"  2^>^&1^|find "REG_"') do set PYTHONDIR=%%b
)
if "%PYTHONDIR%" == "" goto wrong_python
if "%PYTHONEXE%" == "" set PYTHONEXE=python.exe

echo Using Python at %PYTHONDIR%%PYTHONEXE%
"%PYTHONDIR%%PYTHONEXE%" "%~dp0env_check.py"
if errorlevel 1 goto wrong_python

set PYTHON="%PYTHONDIR%%PYTHONEXE%" %PYTHONFLAGS%
set PYTHONPATH=%~dp0..;%~dp0..\lib;%~dp0..\modules\Native\Module_system 1.171
set IRONPYTHONPATH=%PYTHONPATH%

:: Set this to 1 to generate debugging output as data is read and written.
:: This is mostly useful to diagnose errors when something goes wrong,
:: to quickly figure out what exactly was being read or written. Because
:: of the sheer amount of output, it can slow processing by 10-15 seconds.
:: For the same reason, it's best to redirect it to a file when enabled.
:: Note that all this debugging output goes to stdout, while all the usual
:: diagnostic and error messages, and progress bar, are on stderr, so that
:: these two can be handled separately (e.g. only redirect stdout).
set WARBEND_LOG_DATA=0
goto :eof

:wrong_python
echo Python 2.7 not found - download and install from   1>&2
echo https://www.python.org/downloads                   1>&2
exit /b 1
