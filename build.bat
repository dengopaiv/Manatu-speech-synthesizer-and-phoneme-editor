@echo off
echo Setting up Visual Studio environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
if errorlevel 1 (
    echo Failed to set up VS environment
    exit /b 1
)
echo VS environment set up successfully

cd /d "C:\git\NVSpeechPlayer"
echo Running scons in %CD%...
scons
echo Done with exit code %ERRORLEVEL%
