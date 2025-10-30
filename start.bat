@echo off
chcp 65001 >nul
echo ================================================
echo   Campus Help 快速啟動腳本
echo   Streamlit 版本
echo ================================================
echo.

:: 檢查是否在正確的目錄
if not exist "app.py" (
    echo ❌ 錯誤: 找不到 app.py
    echo    請確保在正確的目錄執行此腳本
    pause
    exit /b 1
)

:: 檢查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 錯誤: 找不到 Python
    echo    請先安裝 Python 3.9+
    pause
    exit /b 1
)

echo 🔍 檢查依賴套件...
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo.
    echo 📦 偵測到缺少依賴套件，正在安裝...
    pip install -r requirements.txt
    
    if errorlevel 1 (
        echo ❌ 套件安裝失敗
        pause
        exit /b 1
    )
    
    echo ✅ 套件安裝完成
    echo.
)

:: 檢查資料庫
if not exist "campus_help.db" (
    echo 🗄️ 偵測到資料庫不存在，正在初始化...
    python init_db.py
    echo.
)

:: 啟動應用
echo 🚀 啟動 Campus Help...
echo.
echo ================================================
echo   應用運行於: http://localhost:8501
echo   按 Ctrl+C 停止服務
echo ================================================
echo.
echo 📝 測試帳號:
echo    - 王小美 (資訊管理學系)
echo    - 李大明 (企業管理學系)
echo    - 陳小華 (英文學系)
echo    - 張志明 (數學系)
echo.
streamlit run app.py
