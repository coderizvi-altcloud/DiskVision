@echo off
title Disk Infogetter - Launcher
color 0F
cls
echo.
echo   Starting Disk Infogetter...
echo.
start "Disk Infogetter" cmd /k cd /d "E:\Disk Infogetter" ^&^& ".venv\Scripts\python.exe" main.py
