@echo off
chcp 65001
:: 修改窗口颜色（0A 是黑底绿字，类似黑客帝国；3F 是蓝底白字）
color 3F
:: 修改窗口标题
title 智慧酒店管理系统 - 监控中心
:: 修改窗口大小（列,行）
mode con cols=80 lines=25

cls
echo ==================================================
echo.
echo          智慧酒店管理系统 (智慧后勤版)
echo.
echo           系统正在初始化，请稍候...
echo.
echo ==================================================

:: 1. 确定根目录（即文件夹 '毕业设计' 的位置）
set ROOT_DIR=%~dp0

echo ==========================================
echo    正在检测环境并启动后端...
echo ==========================================

:: 2. 强制进入后端文件夹并用“绝对路径”启动 Python
cd /d "%ROOT_DIR%backend"
if exist ".venv\Scripts\python.exe" (
    :: 使用 start 并在新窗口运行，同时强制指定主机和端口
    start "Hotel-Backend" cmd /k ".venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8001"
) else (
    echo [错误] 在 %ROOT_DIR%backend 下没找到 venv 环境！
    pause
    exit
)

timeout /t 5

echo [2/2] 正在启动前端...
cd /d "%ROOT_DIR%frontend"
if exist "package.json" (
    start "Hotel-Frontend" cmd /k "npm run dev"
) else (
    echo [错误] 在 %ROOT_DIR%frontend 下没找到 package.json！
    pause
    exit
)

timeout /t 5
start http://localhost:5173