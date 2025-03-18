#!/bin/bash

# 設置環境變數以禁用Python的SSL驗證 (僅在開發環境中使用)
export PYTHONHTTPSVERIFY=0
# 或使用以下環境變數
export REQUESTS_CA_BUNDLE=""
export SSL_CERT_FILE=""

# 啟動Django開發伺服器
echo "啟動Django開發伺服器 (已禁用SSL驗證)..."
python manage.py runserver 