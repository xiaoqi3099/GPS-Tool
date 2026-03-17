# GPS经纬度转换工具 - Android APK构建指南

## 快速构建APK（推荐方案）

由于Buildozer需要Linux环境，请按以下步骤使用GitHub Actions自动构建：

### 步骤1: 创建GitHub仓库

1. 访问 https://github.com/new
2. 创建一个新仓库，命名为 `gps-tool`
3. 将 `gps_android` 文件夹内容上传到仓库

### 步骤2: 自动构建APK

1. 进入您的GitHub仓库
2. 点击 `Actions` 标签
3. 点击 `Build Android APK` 工作流
4. 点击 `Run workflow` 按钮
5. 等待构建完成（约15-20分钟）

### 步骤3: 下载APK

1. 构建完成后，在Artifacts中找到 `gps-tool.apk`
2. 下载并安装到Android手机

---

## 项目包含的功能

✅ 单个地址转经纬度  
✅ 批量地址转换（Excel/TXT/CSV）  
✅ BD-09 → GCJ-02 → WGS84坐标系转换  
✅ 进度条显示  
✅ Excel报告导出  

---

## 百度API说明

当前使用的是测试API密钥，如需更换请修改 `baidu_api.py` 中的 `ak` 参数。

申请新的API密钥：https://lbsyun.baidu.com/
