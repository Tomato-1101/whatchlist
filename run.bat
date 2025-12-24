@echo off
REM 仮想環境を有効化してインタラクティブモードで起動

call venv\Scripts\activate.bat
python -m src.main

pause
