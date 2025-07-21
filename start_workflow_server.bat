@echo off
cd %~dp0
cd merged-project-flask\scripts\workflow
python run_workflow_server.py --port 8000
pause 