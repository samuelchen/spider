
:: scrapy need cryptography. For window,
:: install OpenSSL for Window: https://slproweb.com/products/Win32OpenSSL.html (better use win32 version)
set INCLUDE=C:\OpenSSL-Win32\include;
set LIB=C:\OpenSSL-Win32\lib;
pip install cryptography


# twisted for win (scrapy)
pip install Twisted[windows_platform]


pip install scrapy sqlalchemy Pillow

:: psycopg2 for window
:: download : download from http://www.stickpeople.com/projects/python/win-psycopg/
:: easy_install psycopg2-windows.xxx.exe
pip install git+https://github.com/nwcell/psycopg2-windows.git@win32-py34#egg=psycopg2

pip install django<2.0.0
