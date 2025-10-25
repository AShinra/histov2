@echo off
rem Activate virtual environment (if applicable)
call "C:\Athan\Projects\Python\histov2\.venv\Scripts\activate.bat"

rem Navigate to your Streamlit app directory
cd "C:\Athan\Projects\Python\histov2"

rem Run the Streamlit app
streamlit run home.py

pause