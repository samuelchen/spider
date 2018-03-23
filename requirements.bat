@echo off
:: scrapy need cryptography. For window,
:: install OpenSSL for Window: https://slproweb.com/products/Win32OpenSSL.html (better use win32 version)
set INCLUDE=C:\OpenSSL-Win32\include;
set LIB=C:\OpenSSL-Win32\lib;
pip install cryptography



pip install sqlalchemy Pillow

:: psycopg2 for window
:: download : download from http://www.stickpeople.com/projects/python/win-psycopg/
:: easy_install psycopg2-windows.xxx.exe
pip install git+https://github.com/nwcell/psycopg2-windows.git@win32-py34#egg=psycopg2

:: pip install django<2.0.0
pip install django==1.11.* django-allauth



:: twisted for win (scrapy)
@echo "================================================================================
@echo "For Twisted on window, visit https://www.lfd.uci.edu/~gohlke/pythonlibs/#twisted"
@echo "    none-official twisted package.
@echo "================================================================================
:: pip install Twisted[windows_platform]

pause
pip install scrapy