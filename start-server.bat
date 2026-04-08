@echo off
CD /D C:\Users\xiute\Desktop\saulo-v2
call venv\Scripts\activate.bat
python -m uvicorn main:app --host 127.0.0.1 --port 8090 --reload