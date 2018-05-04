@echo off

:: Set VS version
::SET VS90COMNTOOLS=%VS100COMNTOOLS%
::SET VS90COMNTOOLS=%VS110COMNTOOLS%
SET VS90COMNTOOLS=%VS140COMNTOOLS%
::setenv /x64 /release
set MSSDK=1
set DISTUTILS_USE_SDK=1

C:\Python27\python.exe setup.py build
if errorlevel 0 (
    copy build\lib.win32-2.7\pyvicon.pyd .\
)
echo %errorlevel%
pause
