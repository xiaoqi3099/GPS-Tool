@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo 正在初始化Git仓库...
git init
git config user.email "xiaoqi3099@github.com"
git config user.name "xiaoqi3099"

echo.
echo 正在添加文件...
git add -A

echo.
echo 正在提交...
git commit -m "GPS经纬度转换工具 - Android版本"

echo.
echo 正在重命名分支...
git branch -M main

echo.
echo 正在添加远程仓库...
git remote add origin https://github.com/xiaoqi3099/qiqiku.git

echo.
echo ========================================
echo   准备推送到GitHub
echo   请在弹出的窗口中登录GitHub
echo ========================================
echo.

git push -u origin main

echo.
echo ========================================
echo   推送完成！
echo ========================================
pause
