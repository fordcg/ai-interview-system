#!/bin/bash
echo "启动工作流服务器..."
cd "$(dirname "$0")/merged-project-flask/scripts/workflow"
python run_workflow_server.py --port 8000 