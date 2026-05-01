# ikuuu.win 自动签到脚本

> 一行命令搞定每日签到，无需浏览器自动化，零依赖（仅需 `requests`）。

## ✨ 特性

- **一键签到** — 双击 `run.bat` 即可
- **Cookie 过期自动引导** — 30 秒内从浏览器复制粘贴搞定
- **定时任务支持** — 配合 Windows 任务计划程序，每天自动签到
- **日志记录** — 所有操作自动写入 `checkin.log`
- **纯 Python** — 不依赖 Selenium / Playwright，不被验证码困扰

## 📦 文件结构

```
ikuuu_sign/
├── run.bat              # 双击运行
├── setup_task.bat       # 定时任务一键设置
├── config.json          # 配置文件
├── ikuuu_cookies.txt    # Cookie（自动生成）
├── checkin.log          # 运行日志（自动生成）
├── README.md
├── src/
│   └── ikuuu_sign.py    # 源码（跨平台，需要 Python + requests）
└── dist/
    └── ikuuu_sign.exe   # Windows 编译版（无需 Python）
```

### 多端使用

| 平台 | 方式 |
|------|------|
| **Windows** | 双击 `run.bat` 或 `dist/ikuuu_sign.exe` |
| **Linux/macOS** | `python src/ikuuu_sign.py` |
| **定时任务** | `python src/ikuuu_sign.py -s` 或 `dist/ikuuu_sign.exe -s` |

## 🚀 快速开始

### 1. 安装依赖

```bash
pip install requests
```

### 2. 首次获取 Cookie

双击 `run.bat`，脚本检测到无 Cookie 会自动弹出引导：

```
╔══════════════════════════════════════════╗
║         获取 Cookie（30 秒搞定）          ║
╠══════════════════════════════════════════╣
║  1. 浏览器打开 https://ikuuu.win         ║
║  2. 登录账号，勾选 Remember Me           ║
║  3. 按 F12 → 点击 Console 标签           ║
║  4. 输入：copy(document.cookie) → 回车   ║
║  5. 自动打开 ikuuu_cookies.txt           ║
║  6. Ctrl+V 粘贴 → Ctrl+S 保存            ║
╚══════════════════════════════════════════╝
```

按回车后自动完成签到。

### 3. 每日签到

之后每天只需双击 `run.bat` 即可自动签到。

## ⏰ 设置定时签到

右键 `setup_task.bat` → **以管理员身份运行**，创建每天 08:00 自动签到的计划任务。

日志写入 `checkin.log`，可随时查看。

## ⚙️ 配置说明

`config.json`：

```json
{
    "site": {
        "base_url": "https://ikuuu.win"
    }
}
```

| 字段 | 说明 |
|------|------|
| `site.base_url` | 网站地址，一般不用改 |

## ❓ 常见问题

### Cookie 能用多久？

| Cookie | 类型 | 有效期 |
|--------|------|--------|
| `uid` / `key` / `email` / `ip` | 身份令牌 | 约 **7 天** |
| `expire_in` | 过期时间戳 | 服务端控制 |

脚本顶部会实时显示 Cookie 状态（"有效 · 3h前" / "已过期"），过期后自动弹出引导重新获取。

### 为什么不用 Selenium 自动登录？

网站使用 **Geetest v4**（极验）人机验证，Selenium 自动化浏览器会被检测封禁（返回 60500 错误）。Cookie 方案直接绕过验证码，更稳定可靠。

### 为什么不直接从浏览器数据库读取 Cookie？

Chrome/Edge 新版使用 **v20 加密**（App-Bound Encryption）存储 Cookie，纯 Python 无法解密。`copy(document.cookie)` 直接获取浏览器已解密的值，是最简单可靠的方式。

### 签到接口是什么？

```
POST https://ikuuu.win/user/checkin
Headers:
  X-Requested-With: XMLHttpRequest
  Referer: https://ikuuu.win/user
  Cookie: uid=...; key=...
```

无需请求体，认证通过 Cookie 中的 `uid` + `key` 完成。

## 📄 License

MIT

---

## 🔧 开发者：发布新版本

```bash
# 1. 修改完代码后
git add -A && git commit -m "feat: xxx"

# 2. 打 tag 推送，GitHub Actions 自动构建并发布 Release
git tag v1.0.0
git push origin main --tags
```

CI 会在 `dist/` 生成 `ikuuu_sign.exe` 并自动附加到 Release。
