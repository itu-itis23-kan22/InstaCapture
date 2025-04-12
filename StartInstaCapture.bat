@echo off
title InstaCapture - Instagram Downloader
color 0B

:: Set current directory
cd /d "%~dp0"

echo [34m📲 InstaCapture - Instagram Icerık Indirme Araci baslatiliyor...[0m
echo.

:: Check Python installation
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [31mPython bulunamadi! Lutfen Python 3 kurulu oldugundan emin olun.[0m
    echo https://www.python.org/downloads/ adresinden Python 3'u indirebilirsiniz.
    echo.
    pause
    exit /b 1
)

:: Install required packages
echo [34mGerekli paketler kontrol ediliyor...[0m
python -m pip install --quiet --upgrade pip
python -m pip install --quiet pillow requests lxml 
echo.

:: Start GUI
echo [32mGUI baslatiliyor...[0m
python run_gui.py

:: Wait on error
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [31mUygulama baslatilirken bir hata olustu.[0m
    pause
    exit /b 1
) 