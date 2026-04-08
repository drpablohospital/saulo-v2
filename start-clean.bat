@echo off
CD /D C:\Users\xiute\Desktop\saulo-v2
call venv\Scripts\activate.bat
python -c "
import uvicorn
from main import app
uvicorn.run(app, host='127.0.0.1', port=8095, reload=False)
"