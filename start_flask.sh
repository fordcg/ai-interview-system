#!/bin/bash
echo "启动Flask后端服务器..."
cd "$(dirname "$0")/merged-project-flask"
python app.py 