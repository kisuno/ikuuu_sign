# ikuuu 自动签到

> 每日签到，支持 Windows / Linux / macOS。从 ikuuu.one 动态解析可用域名。
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
║  1. 浏览器打开当前域名并登录              ║
║  2. 勾选 Remember Me                    ║
║  3. F12 → Console → 输入:               ║
║     copy(document.cookie) → 回车        ║
║  4. 回终端，右键粘贴 → 回车              ║
╚══════════════════════════════════════════╝
```

之后每次运行自动签到，Cookie 过期自动引导刷新。

## ⏰ 定时签到

| 平台 | 方式 |
|------|------|
| Linux/macOS | `crontab -e` 添加 `0 8 * * * /path/to/ikuuu_sign -s` |
| Windows | 双击 `setup_task.bat`（管理员），每天 08:00 自动签到 |

## ⚙️ 配置

`config.json`：

```json
{
    "site": {
        "base_url": "https://ikuuu.one"
    },
    "cookie": "uid=xxx; email=xxx; key=xxx; ip=xxx; expire_in=xxx",
    "domains": ["ikuuu.one", "ikuuu.win", "ikuuu.fyi"]
}
```

| 字段 | 说明 |
|------|------|
| `site.base_url` | 当前域名 |
| `cookie` | 登录凭据，终端粘贴即可 |
| `domains` | 域名池（由解析器自动更新） |

## 🔍 域名解析

内置 `src/ikuuu_parser.py` 从 ikuuu.one 动态解析当前可用域名，纯 `requests` 实现：

```
ikuuu.one  JS 碎片解码 → .win + .fyi → 生成 ikuuu.win / ikuuu.fyi
```

域名池自动更新写入 `config.json`，无需手动维护。

## ❓ FAQ

**Cookie 能用多久？** 约 7 天，过期后脚本自动引导刷新。

**域名变了怎么办？** 解析器自动从 ikuuu.one 提取最新域名，探测可用后自动切换。

**为什么不自动登录？** 网站使用 Geetest v4 验证码，Cookie 方案直接绕过。

## 🔧 开发

```bash
# 运行解析器
python src/ikuuu_parser.py --json

# 发布新版本
git tag v1.0.5
git push origin main --tags
```

推送 tag 后 GitHub Actions 自动编译 5 个架构并发布 Release。

## 📄 License

MIT
