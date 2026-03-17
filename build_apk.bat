@echo off
echo ========================================
echo   GPS经纬度转换工具 - APK构建脚本
echo ========================================

echo.
echo [1/5] 检查Python环境...
python --version
if errorlevel 1 (
    echo 错误: 未找到Python，请先安装Python 3.8+
    pause
    exit /b 1
)

echo.
echo [2/5] 安装Kivy及相关依赖...
pip install kivy==2.1.0

echo.
echo [3/5] 安装项目依赖...
pip install requests openpyxl xlrd

echo.
echo [4/5] 检查Buildozer...
python -c "import buildozer" 2>nul
if errorlevel 1 (
    echo 正在安装Buildozer...
    pip install buildozer
)

echo.
echo [5/5] 检查Android SDK...
echo 请确保已安装Android SDK并配置ANDROID_SDK_ROOT环境变量
echo.

echo ========================================
echo   环境配置完成！
echo ========================================
echo.
echo 构建APK命令:
echo   cd gps_android
echo   buildozer android debug
echo.
echo 或使用简化命令:
echo   buildozer android
echo.
pause
