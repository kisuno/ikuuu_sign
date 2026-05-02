# ikuuu.win 自动签到脚本

> 一行命令搞定每日签到，无需浏览器自动化。
>
> *Built with [DeepSeek V4 Pro](https://deepseek.com/)*

## 📥 下载

| 平台 | 下载 |
|------|------|
| 🪟 Windows | [ikuuu_sign-windows.exe](https://github.com/kisuno/ikuuu_sign/releases/latest) |
| 🐧 Linux | [ikuuu_sign-linux](https://github.com/kisuno/ikuuu_sign/releases/latest) |
| 🍎 macOS | [ikuuu_sign-macos](https://github.com/kisuno/ikuuu_sign/releases/latest) |

> 编译版 **无需安装 Python 或任何依赖**，下载即用。
> 也可以从源码运行：`pip install requests && python src/ikuuu_sign.py`

## ✨ 特性

- **一键签到** — 双击 exe 或运行 Python 脚本
- **Cookie 过期自动引导** — 30 秒内从浏览器复制粘贴搞定
- **定时任务支持** — 配合 cron / 任务计划程序，每天自动签到
- **日志记录** — 所有操作自动写入 `checkin.log`
- **跨平台** — Windows / Linux / macOS 均可使用

## 🚀 快速开始

### 首次获取 Cookie

运行程序，脚本检测到无 Cookie 会自动弹出引导：

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

若剪贴板已有有效 Cookie，脚本会自动检测并确认。

保存后自动完成签到。

### 每日签到

之后每次运行即可自动签到，无需任何操作。

### 定时签到

| 平台 | 命令 |
|------|------|
| Linux/macOS | `crontab -e` 添加 `0 8 * * * /path/to/ikuuu_sign-linux -s` |
| Windows | 右键 `setup_task.bat` → 管理员运行 |

静默模式 `-s` 仅写日志，不弹窗。

## 📦 文件结构

```
ikuuu_sign/
├── src/ikuuu_sign.py      # 源码（跨平台）
├── dist/                   # 编译产物（由 CI 生成）
├── run.bat                 # Windows 一键启动
├── setup_task.bat          # Windows 定时任务
├── config.json             # 配置文件
├── ikuuu_cookies.txt       # Cookie（自动生成）
└── checkin.log             # 日志（自动生成）
```

## ⚙️ 配置

```json
{
    "site": {
        "master_url": "https://ikuuu.one",
        "base_url": "https://ikuuu.win"
    },
    "cookie": {
        "file": "ikuuu_cookies.txt"
    }
}
```

| 字段 | 说明 |
|------|------|
| `site.master_url` | 主域名，自动探测当前可用域名 |
| `site.base_url` | 当前域名（自动更新） |
| `cookie.file` | Cookie 文件路径 |

启动时自动从主域名探测，支持 18 个已知域名的自动切换。`--fetch` 强制重新探测。

## ❓ 常见问题

### Cookie 能用多久？

| Cookie | 有效期 |
|--------|--------|
| `uid` / `key` / `email` / `ip` | 约 7 天 |
| `expire_in` | 服务端控制 |

过期后运行脚本会自动引导重新获取。

### 为什么不用 Selenium 自动登录？

网站使用 **Geetest v4** 人机验证，自动化浏览器会被封禁。Cookie 方案直接绕过验证码，稳定可靠。

### 签到接口

```
POST https://ikuuu.win/user/checkin
Cookie: uid=...; key=...
```

认证通过 `uid` + `key` 完成，无需密码。

## 🔧 开发者

```bash
pip install requests
python src/ikuuu_sign.py       # 交互模式
python src/ikuuu_sign.py -s    # 静默模式
```

### 发布新版本

```bash
git tag v1.0.0
git push origin main --tags
```

GitHub Actions 自动编译 Windows / Linux / macOS 三平台并发布 Release。

## 📄 License

MIT
