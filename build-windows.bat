@echo off
REM ============================================================
REM  Tao file cai dat Windows: ads_config_generator.exe
REM  YEU CAU: cai Python 3.10-3.12 tu python.org (tick "Add to PATH").
REM  Cach dung: chep ca thu muc nay sang may Windows -> double-click file nay.
REM ============================================================
setlocal
cd /d "%~dp0"

echo [1/3] Tao moi truong ao...
py -m venv build-venv 2>nul || python -m venv build-venv
call build-venv\Scripts\activate.bat

echo [2/3] Cai PyInstaller...
python -m pip install --upgrade pip pyinstaller

echo [3/3] Build exe...
python -m PyInstaller --onefile --windowed --name ads_config_generator ads_config_generator.py

echo.
echo ============================================================
echo  XONG! File cai dat: dist\ads_config_generator.exe
echo  (chay truc tiep, khong can cai Python tren may khac)
echo ============================================================
pause
