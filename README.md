# Codex Weekly Usage · Codex 周用量

在 Windows Codex 桌面客户端输入框下方显示账号周额度。通过本机 CDP 注入临时 DOM，不修改客户端安装文件。

社区实验工具，非 OpenAI 官方插件。需要 Windows 10/11、Python 3.10+、已安装并登录的 Microsoft Store Codex 桌面客户端。

## 安装

```console
python -m pip install -r requirements.txt
python launch.pyw
```

也可以双击 launch.pyw。它自动发现商店安装路径，启动带 CDP 的 Codex 窗口与后台监控。可能会多开一个 Codex 窗口。已运行时尝试切回调试窗口。

运行 `python create_shortcut.py` 创建新的桌面快捷方式，不覆盖已有快捷方式。图标仅从本机客户端复制到生成的 assets 目录，仓库不分发 OpenAI 图标。

双击 stop.pyw 停止轮询并移除状态行。请求进行中时最多等待约 25 秒。要关闭调试端口，请退出带调试参数的 Codex 实例，然后正常启动官方客户端。没有开机自启。

## 功能

- 每 30 秒刷新账号周额度，显示已用、剩余、重置时间。
- 识别 codex 账号池的 10080 分钟窗口，支持 primary / secondary。
- 失败、超过 90 秒、到重置时间时明确标记，缺失窗口不虚构 100%。
- 真实页面底部元素，输入框切换后重新挂载。
- Windows 商店路径自动识别、任务栏身份恢复、CDP 断线重连。

## 数据和安全

额度来自本机 Codex App Server 的 account/rateLimits/read，认证及上游请求由官方 Codex 处理。不用 Token 数估算额度，不直接读取登录令牌，不读取聊天日志，不上传会话。

CDP 监听 127.0.0.1:9222，它是能控制页面的本机调试接口。不要转发端口、绑定公网或分享调试地址；其他本机进程可能访问它。

weekly-monitor-status.json 保存最近额度及界面结果，weekly-monitor.log 保存错误，weekly-monitor.stop 是停止标记。均被 Git 忽略，退出后不自动删除诊断文件。

## 限制

已在作者的 Windows 商店版 Codex 26.1016、26.1023 验证注入和显示。仅支持 Windows、单个主要 Codex 页面、固定端口 9222。多窗口、其他安装渠道、未来更新需单独验证。依赖商店注册表和本机 Codex bin 缓存。界面结构和调试接口可能随更新变化。

## 测试

```console
python -m unittest discover -s tests -v
```

自动测试不访问账号、不启动客户端，实际 UI 和登录环境需另行验证。

## 许可与致谢

MIT。CDP 传输及页面选择改编自 [KevinKE93/Codex-Monitor](https://github.com/KevinKE93/Codex-Monitor)，保留 Kevin Ke 版权声明。新增 Windows 启动、周额度读取和底部状态行。详见 THIRD_PARTY_NOTICES.md。
