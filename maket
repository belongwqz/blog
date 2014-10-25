echo off
title tool
color 1e
cls
if exist .\dist\ rmdir /s /q .\dist\
if exist .\build\ rmdir /s /q .\build\
if exist .\Output\ rmdir /s /q .\Output\
python setup.py
iscc install.iss
echo It will automatically exit!
ping 127.0.0.1>nul
