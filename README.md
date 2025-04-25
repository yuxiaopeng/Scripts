# Scripts 工程

这个仓库包含了各种实用的 Python 脚本，用于自动化和系统管理任务。

## 脚本列表

| 脚本名 | 作用 | 使用方式 |
|--------|------|----------|
| ip_monitor.py | 监控外网 IP 变化并通过 iMessage 发送通知。支持检测 VPN 状态（包括 Clash Verge）并区分原始 IP 和代理 IP。 | `python3 ip_monitor.py` |

## 详细说明

### ip_monitor.py

**功能**：
- 定期检查外网 IP 地址是否发生变化
- 检测 VPN 或代理（如 Clash Verge）是否启用
- 当 IP 变化时通过 iMessage 发送通知
- 同时监控原始 IP 和代理后的 IP

**配置**：
- 在脚本开头修改 `RECIPIENT` 变量为你的 iMessage 联系人
- 可调整 `CHECK_INTERVAL` 变量修改检查频率（默认 300 秒）

**依赖**：
```bash
pip3 install requests
```
