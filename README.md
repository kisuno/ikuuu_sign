# ikuuu.win 自动签到

> 每日签到，一行命令。支持 Windows / Linux / macOS。
>
> *Built with [DeepSeek V4 Pro](https://deepseek.com/)*

## 📥 安装

### 预编译版本（推荐，无需 Python）

从 [Releases](https://github.com/kisuno/ikuuu_sign/releases) 下载对应架构：

| 平台 | 架构 | 文件 |
|------|------|------|
| 🪟 Windows | x64 | `ikuuu_sign-windows-amd64.exe` |
| 🐧 Linux | x64 | `ikuuu_sign-linux-amd64` |
| 🐧 Linux | ARM64 | `ikuuu_sign-linux-arm64` |
| 🍎 macOS | x64 (Intel) | `ikuuu_sign-macos-amd64` |
| 🍎 macOS | ARM64 (M1/M2/M3) | `ikuuu_sign-macos-arm64` |

下载后双击（Windows）或在终端运行：

```bash
# Linux/macOS
chmod +x ikuuu_sign-linux-amd64
./ikuuu_sign-linux-amd64

# 静默模式（定时任务）
./ikuuu_sign-linux-amd64 -s
```

### 源码运行（需要 Python 3）

```bash
pip install requests
python src/ikuuu_sign.py
```

## 🚀 快速开始

首次运行会提示获取 Cookie：

```
╔══════════════════════════════════════════╗
║         获取 Cookie（30 秒搞定）          ║
╠══════════════════════════════════════════╣
║  1. 浏览器打开 https://ikuuu.win         ║
║  2. 登录，勾选 Remember Me              ║
║  3. F12 → Console → 输入:               ║
║     copy(document.cookie) → 回车        ║
║  4. 回终端，右键粘贴 → 回车              ║
╚══════════════════════════════════════════╝
```

之后每次运行自动签到。

## ⏰ 定时签到

| 平台 | 方式 |
|------|------|
| Linux/macOS | `crontab -e` 添加 `0 8 * * * /path/to/ikuuu_sign -s` |
| Windows | 双击 `setup_task.bat`（管理员），每天 08:00 自动签到 |

## ⚙️ 配置

所有配置（含 Cookie）都在 `config.json`：

```json
{
    "site": {
        "base_url": "https://ikuuu.win"
    },
    "cookie": "uid=xxx; email=xxx; key=xxx; ip=xxx; expire_in=xxx"
}
```

| 字段 | 说明 |
|------|------|
| `site.base_url` | 当前域名（自动探测 18 个域名切换） |
| `cookie` | 登录凭据，从浏览器 Ctrl+V 粘贴 |

## ❓ FAQ

**Cookie 能用多久？** 约 7 天，过期后运行脚本自动引导刷新。

**域名变了怎么办？** ikuuu.one 为主域名，其他域名不可用时脚本会提示输入新域名。也可手动修改 `config.json` 中的 `base_url`。

**为什么不自动登录？** 网站使用 Geetest v4 验证码，Cookie 方案直接绕过。

## 🔧 开发

```bash
git tag v1.0.2
git push origin main --tags
```

推送 tag 后 GitHub Actions 自动编译 5 个架构并发布 Release。

## 📄 License

MIT
