"""
明日方舟终末地 UID 查询工具
自动打开鹰角网络用户中心，监控网络请求并提取UID信息
"""

import sys
import json
import re
import os
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
    QWidget, QTextEdit, QPushButton, QLabel, QSplitter,
    QFrame, QMessageBox, QToolTip
)
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QDesktopServices, QPixmap, QCursor
from PyQt5.QtCore import Qt, QUrl, pyqtSlot
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEnginePage
from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor
from PyQt5.QtNetwork import QNetworkAccessManager, QNetworkRequest


class NetworkInterceptor(QWebEngineUrlRequestInterceptor):
    """网络请求拦截器"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        # 记录所有请求URL
        if self.main_window:
            self.main_window.log_request(url)


class CustomWebPage(QWebEnginePage):
    """自定义网页类，用于处理JavaScript消息"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.main_window = parent
        
    def javaScriptConsoleMessage(self, level, message, lineNumber, sourceID):
        # 捕获console消息
        pass


class UIDQueryTool(QMainWindow):
    def __init__(self):
        super().__init__()
        self.uid_list = []
        self.request_log = []
        self.init_ui()
        self.setup_browser()
        
    def init_ui(self):
        """初始化UI界面"""
        self.setWindowTitle("明日方舟终末地 UID 查询工具")
        self.setGeometry(100, 100, 1400, 900)
        
        # 设置窗口图标
        self.set_window_icon()
        
        # 主窗口部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QHBoxLayout(central_widget)
        
        # 创建分割器
        splitter = QSplitter(Qt.Horizontal)
        
        # 左侧：浏览器区域
        browser_frame = QFrame()
        browser_frame.setFrameStyle(QFrame.StyledPanel)
        browser_layout = QVBoxLayout(browser_frame)
        
        # 浏览器视图
        self.browser = QWebEngineView()
        browser_layout.addWidget(self.browser)
        
        # 右侧：UID信息显示区域
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_frame.setMinimumWidth(400)
        info_layout = QVBoxLayout(info_frame)
        
        # UID显示标题
        uid_title = QLabel("📋 检测到的 UID 信息")
        uid_title.setFont(QFont("Microsoft YaHei", 14, QFont.Bold))
        uid_title.setStyleSheet("color: #2196F3; padding: 10px;")
        info_layout.addWidget(uid_title)
        
        # UID显示区域
        self.uid_display = QTextEdit()
        self.uid_display.setReadOnly(True)
        self.uid_display.setFont(QFont("Consolas", 11))
        self.uid_display.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #00ff00;
                border: 2px solid #333;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.uid_display.setPlaceholderText("等待检测 UID 信息...\n\n操作步骤：\n1. 在左侧浏览器中登录鹰角账号\n2. 点击「角色绑定」\n3. UID信息将自动显示在此处")
        info_layout.addWidget(self.uid_display)
        
        # 复制按钮
        copy_btn = QPushButton("📋 复制所有 UID")
        copy_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        copy_btn.clicked.connect(self.copy_uids)
        info_layout.addWidget(copy_btn)
        
        # 网络请求日志标题
        log_title = QLabel("🌐 网络请求日志 (监控中...)")
        log_title.setFont(QFont("Microsoft YaHei", 12, QFont.Bold))
        log_title.setStyleSheet("color: #FF9800; padding: 10px; margin-top: 10px;")
        info_layout.addWidget(log_title)
        
        # 网络请求日志区域
        self.log_display = QTextEdit()
        self.log_display.setReadOnly(True)
        self.log_display.setFont(QFont("Consolas", 9))
        self.log_display.setMaximumHeight(200)
        self.log_display.setStyleSheet("""
            QTextEdit {
                background-color: #2d2d2d;
                color: #aaaaaa;
                border: 1px solid #444;
                border-radius: 3px;
                padding: 5px;
            }
        """)
        info_layout.addWidget(self.log_display)
        
        # 联系信息容器
        contact_frame = QFrame()
        contact_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                border-radius: 5px;
                margin-top: 10px;
            }
        """)
        contact_layout = QVBoxLayout(contact_frame)
        contact_layout.setContentsMargins(10, 10, 10, 10)
        
        # B站链接
        bilibili_btn = QPushButton("📺 B站：54006o")
        bilibili_btn.setStyleSheet("""
            QPushButton {
                background-color: #fb7299;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #e85a7e;
            }
        """)
        bilibili_btn.setCursor(QCursor(Qt.PointingHandCursor))
        bilibili_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://space.bilibili.com/74017636")))
        contact_layout.addWidget(bilibili_btn)
        
        # QQ群链接容器
        qq_layout = QHBoxLayout()
        
        # QQ群按钮
        self.qq_btn = QPushButton("💬 终末地QQ群：1075769890")
        self.qq_btn.setStyleSheet("""
            QPushButton {
                background-color: #12b7f5;
                color: white;
                border: none;
                padding: 8px 15px;
                font-size: 12px;
                border-radius: 4px;
                text-align: left;
            }
            QPushButton:hover {
                background-color: #0ea5e0;
            }
        """)
        self.qq_btn.setCursor(QCursor(Qt.PointingHandCursor))
        self.qq_btn.clicked.connect(lambda: QDesktopServices.openUrl(QUrl("https://qm.qq.com/q/Ksqc088ZCo")))
        self.qq_btn.enterEvent = self.show_qq_qrcode
        self.qq_btn.leaveEvent = self.hide_qq_qrcode
        qq_layout.addWidget(self.qq_btn)
        
        # 复制群号按钮
        copy_qq_btn = QPushButton("📋")
        copy_qq_btn.setFixedWidth(40)
        copy_qq_btn.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px;
                font-size: 12px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        copy_qq_btn.setCursor(QCursor(Qt.PointingHandCursor))
        copy_qq_btn.setToolTip("复制群号")
        copy_qq_btn.clicked.connect(self.copy_qq_group)
        qq_layout.addWidget(copy_qq_btn)
        
        contact_layout.addLayout(qq_layout)
        info_layout.addWidget(contact_frame)
        
        # 加载QQ群二维码
        self.load_qq_qrcode()
        
        # 添加到分割器
        splitter.addWidget(browser_frame)
        splitter.addWidget(info_frame)
        splitter.setSizes([1000, 350])
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        
        main_layout.addWidget(splitter)
        
        # 设置窗口样式
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f5;
            }
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 8px 16px;
                font-size: 12px;
                border-radius: 4px;
                margin: 2px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
    
    def set_window_icon(self):
        """设置窗口图标"""
        # 获取图标路径（支持打包后的路径）
        if getattr(sys, 'frozen', False):
            # 打包后的路径
            base_path = sys._MEIPASS
        else:
            # 开发环境路径
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        icon_path = os.path.join(base_path, 'icon.ico')
        if os.path.exists(icon_path):
            self.setWindowIcon(QIcon(icon_path))
    
    def load_qq_qrcode(self):
        """加载QQ群二维码"""
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.abspath(__file__))
        
        qr_path = os.path.join(base_path, 'qq_group_qr.png')
        if os.path.exists(qr_path):
            self.qq_qrcode = QPixmap(qr_path).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        else:
            self.qq_qrcode = None
    
    def show_qq_qrcode(self, event):
        """显示QQ群二维码"""
        if self.qq_qrcode:
            QToolTip.showText(
                self.qq_btn.mapToGlobal(self.qq_btn.rect().topRight()),
                "",
                self.qq_btn
            )
            # 创建自定义提示窗口
            from PyQt5.QtWidgets import QDialog, QVBoxLayout as QVBox
            if not hasattr(self, 'qr_dialog') or not self.qr_dialog.isVisible():
                self.qr_dialog = QDialog(self, Qt.ToolTip | Qt.FramelessWindowHint)
                self.qr_dialog.setStyleSheet("background-color: white; border: 2px solid #12b7f5; border-radius: 8px; padding: 10px;")
                layout = QVBox(self.qr_dialog)
                qr_label = QLabel()
                qr_label.setPixmap(self.qq_qrcode)
                layout.addWidget(qr_label)
                title = QLabel("扫码加入QQ群")
                title.setAlignment(Qt.AlignCenter)
                title.setStyleSheet("color: #333; font-size: 12px; font-weight: bold;")
                layout.addWidget(title)
                
                pos = self.qq_btn.mapToGlobal(self.qq_btn.rect().topRight())
                self.qr_dialog.move(pos.x() + 10, pos.y() - 50)
                self.qr_dialog.show()
    
    def hide_qq_qrcode(self, event):
        """隐藏QQ群二维码"""
        if hasattr(self, 'qr_dialog') and self.qr_dialog.isVisible():
            self.qr_dialog.hide()
    
    def copy_qq_group(self):
        """复制QQ群号"""
        clipboard = QApplication.clipboard()
        clipboard.setText("1075769890")
        QMessageBox.information(self, "复制成功", "QQ群号 1075769890 已复制到剪贴板")
        
    def setup_browser(self):
        """设置浏览器"""
        # 创建自定义页面
        self.page = CustomWebPage(self)
        self.browser.setPage(self.page)
        
        # 设置网络拦截器
        profile = self.browser.page().profile()
        self.interceptor = NetworkInterceptor(self)
        profile.setUrlRequestInterceptor(self.interceptor)
        
        # 连接加载完成信号
        self.browser.loadFinished.connect(self.on_load_finished)
        
        # 注入JavaScript来监控XHR请求
        self.browser.page().loadFinished.connect(self.inject_monitor_script)
        
        # 加载目标页面
        self.browser.setUrl(QUrl("https://user.hypergryph.com/"))
        
    def inject_monitor_script(self, ok):
        """注入JavaScript监控脚本"""
        if not ok:
            return
            
        # 注入XHR监控脚本
        script = """
        (function() {
            // 保存原始的XHR
            var originalXHR = window.XMLHttpRequest;
            
            // 重写XMLHttpRequest
            window.XMLHttpRequest = function() {
                var xhr = new originalXHR();
                var originalOpen = xhr.open;
                var originalSend = xhr.send;
                
                xhr.open = function(method, url) {
                    xhr._url = url;
                    xhr._method = method;
                    return originalOpen.apply(xhr, arguments);
                };
                
                xhr.addEventListener('load', function() {
                    try {
                        var responseText = xhr.responseText;
                        var url = xhr._url || '';
                        
                        // 检查是否包含UID相关信息
                        if (responseText && (
                            url.indexOf('binding') !== -1 ||
                            url.indexOf('user') !== -1 ||
                            url.indexOf('account') !== -1 ||
                            url.indexOf('game') !== -1 ||
                            responseText.indexOf('uid') !== -1 ||
                            responseText.indexOf('Uid') !== -1 ||
                            responseText.indexOf('UID') !== -1
                        )) {
                            // 通过修改document title来传递数据
                            var data = {
                                url: url,
                                response: responseText.substring(0, 5000)
                            };
                            
                            // 创建自定义事件
                            var event = new CustomEvent('xhrResponse', { detail: data });
                            document.dispatchEvent(event);
                            
                            // 将数据保存到全局变量
                            window.__lastXHRData = window.__lastXHRData || [];
                            window.__lastXHRData.push(data);
                            
                            console.log('XHR_DATA:' + JSON.stringify(data));
                        }
                    } catch(e) {
                        console.log('Error processing XHR:', e);
                    }
                });
                
                return xhr;
            };
            
            // 同时监控fetch请求
            var originalFetch = window.fetch;
            window.fetch = function(url, options) {
                return originalFetch.apply(this, arguments).then(function(response) {
                    var clonedResponse = response.clone();
                    clonedResponse.text().then(function(text) {
                        try {
                            var urlStr = typeof url === 'string' ? url : url.url;
                            if (text && (
                                urlStr.indexOf('binding') !== -1 ||
                                urlStr.indexOf('user') !== -1 ||
                                urlStr.indexOf('account') !== -1 ||
                                urlStr.indexOf('game') !== -1 ||
                                text.indexOf('uid') !== -1 ||
                                text.indexOf('Uid') !== -1 ||
                                text.indexOf('UID') !== -1
                            )) {
                                var data = {
                                    url: urlStr,
                                    response: text.substring(0, 5000)
                                };
                                window.__lastXHRData = window.__lastXHRData || [];
                                window.__lastXHRData.push(data);
                                console.log('FETCH_DATA:' + JSON.stringify(data));
                            }
                        } catch(e) {}
                    });
                    return response;
                });
            };
            
            console.log('Network monitor injected successfully');
        })();
        """
        self.browser.page().runJavaScript(script)
        
        # 定期检查捕获的数据
        from PyQt5.QtCore import QTimer
        if not hasattr(self, 'check_timer'):
            self.check_timer = QTimer(self)
            self.check_timer.timeout.connect(self.check_captured_data)
            self.check_timer.start(1000)  # 每秒检查一次
            
    def check_captured_data(self):
        """检查捕获的数据"""
        script = """
        (function() {
            if (window.__lastXHRData && window.__lastXHRData.length > 0) {
                var data = window.__lastXHRData;
                window.__lastXHRData = [];
                return JSON.stringify(data);
            }
            return null;
        })();
        """
        self.browser.page().runJavaScript(script, self.process_captured_data)
        
    def process_captured_data(self, result):
        """处理捕获的数据"""
        if not result:
            return
            
        try:
            data_list = json.loads(result)
            for data in data_list:
                url = data.get('url', '')
                response = data.get('response', '')
                
                self.log_request(f"[响应] {url}")
                
                # 解析响应中的UID
                self.extract_uid_from_response(response, url)
                
        except Exception as e:
            pass
            
    def extract_uid_from_response(self, response_text, url=""):
        """从响应中提取UID"""
        try:
            # 尝试解析JSON
            data = json.loads(response_text)
            self.find_uid_in_json(data, url)
        except:
            # 非JSON格式，使用正则匹配
            self.find_uid_by_regex(response_text, url)
            
    def find_uid_in_json(self, data, url="", path=""):
        """递归查找JSON中的UID"""
        if isinstance(data, dict):
            for key, value in data.items():
                current_path = f"{path}.{key}" if path else key
                
                # 检查键名是否包含uid
                if 'uid' in key.lower():
                    self.add_uid(str(value), f"JSON路径: {current_path}", url)
                    
                # 递归处理
                if isinstance(value, (dict, list)):
                    self.find_uid_in_json(value, url, current_path)
                    
        elif isinstance(data, list):
            for i, item in enumerate(data):
                current_path = f"{path}[{i}]"
                self.find_uid_in_json(item, url, current_path)
                
    def find_uid_by_regex(self, text, url=""):
        """使用正则表达式查找UID"""
        # 匹配常见的UID格式
        patterns = [
            r'"uid"\s*:\s*"?(\d+)"?',
            r'"Uid"\s*:\s*"?(\d+)"?',
            r'"UID"\s*:\s*"?(\d+)"?',
            r'uid[=:]\s*(\d+)',
            r'userId[=:]\s*"?(\d+)"?',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                self.add_uid(match, f"正则匹配", url)
                
    def add_uid(self, uid, source, url=""):
        """添加UID到列表"""
        if uid and uid not in self.uid_list and len(uid) >= 6:
            self.uid_list.append(uid)
            
            # 更新显示
            display_text = self.uid_display.toPlainText()
            if "等待检测" in display_text or not display_text:
                display_text = ""
                
            timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
            new_entry = f"[{timestamp}] UID: {uid}\n  来源: {source}\n  URL: {url[:80]}...\n\n"
            
            self.uid_display.setText(display_text + new_entry)
            
            # 滚动到底部
            scrollbar = self.uid_display.verticalScrollBar()
            scrollbar.setValue(scrollbar.maximum())
            
            # 弹出提示
            self.statusBar().showMessage(f"发现新UID: {uid}", 5000)
            
    def log_request(self, url):
        """记录网络请求"""
        # 过滤掉一些不重要的请求
        ignore_patterns = ['.png', '.jpg', '.gif', '.css', '.ico', 'google', 'facebook', 'analytics']
        for pattern in ignore_patterns:
            if pattern in url.lower():
                return
                
        if url not in self.request_log:
            self.request_log.append(url)
            
            # 保持日志数量
            if len(self.request_log) > 100:
                self.request_log = self.request_log[-50:]
                
            # 更新日志显示
            timestamp = __import__('datetime').datetime.now().strftime("%H:%M:%S")
            short_url = url[:100] + "..." if len(url) > 100 else url
            self.log_display.append(f"[{timestamp}] {short_url}")
            
    def on_load_finished(self, ok):
        """页面加载完成"""
        if ok:
            self.statusBar().showMessage("页面加载完成", 3000)
        else:
            self.statusBar().showMessage("页面加载失败", 3000)
            
    def refresh_page(self):
        """刷新页面"""
        self.browser.reload()
        
    def go_home(self):
        """返回首页"""
        self.browser.setUrl(QUrl("https://user.hypergryph.com/"))
        
    def clear_logs(self):
        """清除记录"""
        self.uid_list = []
        self.request_log = []
        self.uid_display.clear()
        self.uid_display.setPlaceholderText("等待检测 UID 信息...")
        self.log_display.clear()
        self.statusBar().showMessage("已清除所有记录", 3000)
        
    def copy_uids(self):
        """复制所有UID"""
        if self.uid_list:
            clipboard = QApplication.clipboard()
            clipboard.setText("\n".join(self.uid_list))
            QMessageBox.information(self, "复制成功", f"已复制 {len(self.uid_list)} 个UID到剪贴板")
        else:
            QMessageBox.warning(self, "提示", "暂无UID可复制")


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    # 设置应用信息
    app.setApplicationName("明日方舟终末地 UID 查询工具")
    app.setOrganizationName("ArkUID")
    
    window = UIDQueryTool()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
