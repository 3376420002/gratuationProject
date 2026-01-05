@echo off
echo 正在启动智慧酒店管理系统...

:: 1. 启动后端 (假设你在 venv 虚拟环境下)
start "Hotel-Backend" cmd /k "call venv\Scripts\activate && uvicorn main:app --reload --port 8001"

:: 2. 等待 3 秒确保后端先启动
timeout /t 3

:: 3. 启动前端
start "Hotel-Frontend" cmd /k "npm run dev"

:: 4. 自动打开浏览器访问系统
timeout /t 5
start http://localhost:5174/dashboard

echo 系统已启动！请不要关闭弹出的黑窗口。
pause