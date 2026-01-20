@echo off
chcp 65001 >nul
echo ========================================
echo   明日方舟终末地 UID 查询工具 打包脚本
echo ========================================
echo.

echo [1/2] 检查 PyInstaller...
pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo 正在安装 PyInstaller...
    pip install pyinstaller
)

echo [2/2] 开始打包...
pyinstaller build.spec --clean

echo.
echo ========================================
echo   打包完成！
echo   输出文件: dist\终末地UID查询工具.exe
echo ========================================
pause
