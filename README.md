# 明日方舟终末地 UID 查询工具

<p align="center">
  <img src="icon.ico" alt="Logo" width="80" height="80">
</p>

<p align="center">
  自动打开鹰角网络用户中心，监控网络请求并提取游戏UID信息
</p>

<p align="center">
  <a href="https://github.com/54006/zmduid/releases">
    <img src="https://img.shields.io/github/v/release/54006/zmduid?style=flat-square" alt="Release">
  </a>
  <a href="https://github.com/54006/zmduid/blob/main/LICENSE">
    <img src="https://img.shields.io/github/license/54006/zmduid?style=flat-square" alt="License">
  </a>
  <a href="https://github.com/54006/zmduid/stargazers">
    <img src="https://img.shields.io/github/stars/54006/zmduid?style=flat-square" alt="Stars">
  </a>
</p>

---

## ✨ 功能特点

- 🌐 **内嵌浏览器** - 自动打开鹰角用户中心
- 🔍 **自动监控** - 实时监控所有网络请求
- 📋 **UID提取** - 自动识别并提取UID信息
- 📝 **请求日志** - 网络请求日志记录
- 📎 **一键复制** - 快速复制所有UID

## 📥 下载安装

### 方式一：直接下载（推荐）

前往 [Releases](https://github.com/54006/zmduid/releases) 页面下载最新版本的 `终末地UID查询工具.exe`

### 方式二：从源码运行

```bash
# 克隆仓库
git clone https://github.com/54006/zmduid.git
cd zmduid

# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

## 📖 使用方法

1. **启动程序** - 运行 `终末地UID查询工具.exe` 或 `python main.py`
2. **登录账号** - 在左侧浏览器中登录你的鹰角账号
3. **点击绑定** - 点击左侧菜单的「角色绑定」
4. **查看UID** - UID信息将自动显示在右侧面板

## 🎮 操作说明

| 按钮 | 功能 |
|------|------|
| 🔄 刷新页面 | 重新加载当前页面 |
| 🏠 返回首页 | 返回鹰角用户中心首页 |
| 🗑️ 清除记录 | 清空所有检测到的UID和日志 |
| 📋 复制所有UID | 将检测到的UID复制到剪贴板 |

## 🛠️ 自行打包

```bash
# 安装 PyInstaller
pip install pyinstaller

# 打包
pyinstaller build.spec --clean

# 或直接运行打包脚本
build.bat
```

输出文件位于 `dist/终末地UID查询工具.exe`

## 🔧 技术说明

- 使用 **PyQt5 WebEngine** 实现浏览器功能
- 通过 **JavaScript 注入** 监控 XMLHttpRequest 和 Fetch 请求
- 支持 **JSON解析** 和 **正则匹配** 提取UID

## 📋 依赖

- Python 3.8+
- PyQt5
- PyQtWebEngine

## ⚠️ 注意事项

- 首次运行可能需要较长时间加载 WebEngine 组件
- 请确保网络连接正常
- UID信息来源于网页的网络请求响应
- 本工具仅用于查询自己的UID，请勿用于其他用途

## 📄 开源协议

本项目采用 [MIT License](LICENSE) 开源协议

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
