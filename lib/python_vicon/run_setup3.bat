@echo off

:: Set VS version
::SET VS90COMNTOOLS=%VS100COMNTOOLS%
::SET VS90COMNTOOLS=%VS110COMNTOOLS%
SET VS90COMNTOOLS=%VS140COMNTOOLS%
::setenv /x64 /release
set MSSDK=1
set DISTUTILS_USE_SDK=1

REM C:\WinPython-64bit-3.6.2.0Qt5\python-3.6.2.amd64\python.exe setup.py build
%USERPROFILE%\Miniconda3\python.exe setup.py build
if errorlevel 0 (
    copy C:\Users\Jay\Desktop\PyVicon\python_vicon\build\lib.win32-3.6\pyvicon.cp36-win32.pyd .\pyvicon.pyd
)
echo %errorlevel%
pause
