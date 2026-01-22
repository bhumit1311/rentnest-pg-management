@echo off
echo Starting ResidenceHub - Smart Living Management System...
cd /d "%~dp0"
python -m streamlit run main.py --server.port 8501 --server.address 0.0.0.0
pause