@echo off
echo Setting up Godot build environment...
call "C:\Program Files\Microsoft Visual Studio\2022\Community\VC\Auxiliary\Build\vcvarsall.bat" x64
echo Environment ready for building!
echo.
echo Usage:
echo   cd E:\Dev\godot-dev
echo   scons target=editor platform=windows
echo.
cmd /k
