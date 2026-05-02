#!/usr/bin/env python3
"""
ikuuu.win 每日签到
====================
  run.bat            交互模式（默认），Cookie 过期自动引导
  ikuuu_sign.py -s   静默模式，仅签到写日志（供定时任务）
"""

import os, sys, json, time, logging, argparse
from datetime import datetime
from urllib.parse import unquote
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
os.chdir(SCRIPT_DIR)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
BASE = "https://ikuuu.win"
COOKIE_FILE = os.path.join(SCRIPT_DIR, "ikuuu_cookies.txt")
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# ── 日志（静默模式下仅写文件）────────────
def setup_logging(silent):
    handlers = [logging.FileHandler(os.path.join(SCRIPT_DIR, 'checkin.log'), encoding='utf-8')]
    if not silent:
        handlers.insert(0, logging.StreamHandler())
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s  %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=handlers
    )
    return logging.getLogger(__name__)


# ── 核心逻辑 ─────────────────────────────
def load_config():
    cfg = {"base_url": BASE}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'site' in data:
                cfg['base_url'] = data['site'].get('base_url', BASE)
        except:
            pass
    return cfg


def read_cookies():
    if not os.path.exists(COOKIE_FILE):
        return {}, ""
    with open(COOKIE_FILE, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    cookies = {}
    for item in raw.split(';'):
        item = item.strip()
        if '=' in item:
            k, v = item.split('=', 1)
            if v.strip():
                cookies[k.strip()] = v.strip()
    return cookies, raw


def cookie_status():
    cookies, _ = read_cookies()
    if not cookies:
        return "missing", "未获取"
    if 'uid' not in cookies or 'key' not in cookies:
        return "invalid", "内容不完整"
    try:
        s = requests.Session()
        s.headers['User-Agent'] = UA
        for k, v in cookies.items():
            s.cookies.set(k, v)
        r = s.get(f"{BASE}/user", timeout=8, allow_redirects=False)
        if r.status_code == 200:
            mtime = os.path.getmtime(COOKIE_FILE)
            hours = (time.time() - mtime) / 3600
            return "ok", f"有效 · {hours:.0f}h前"
        return "expired", "已过期"
    except:
        return "unknown", "无法验证"


def do_checkin():
    cookies, _ = read_cookies()
    if not cookies:
        return False, "无 Cookie"

    s = requests.Session()
    s.headers.update({
        'User-Agent': UA,
        'Accept': 'application/json, text/javascript, */*; q=0.01',
    })
    for k, v in cookies.items():
        s.cookies.set(k, v)

    xsrf = cookies.get('XSRF-TOKEN', '')
    if xsrf:
        s.headers['X-XSRF-TOKEN'] = unquote(xsrf)

    try:
        s.get(f"{BASE}/user", timeout=10)
        r = s.post(f"{BASE}/user/checkin", timeout=10, headers={
            'Referer': f"{BASE}/user",
            'X-Requested-With': 'XMLHttpRequest',
        })
        data = r.json()
        ret = data.get('ret', -1)
        msg = data.get('msg', str(data))
        return (True, msg) if ret == 1 else (True, msg)
    except requests.exceptions.JSONDecodeError:
        if 'login' in r.text.lower():
            return False, "Cookie 已失效"
        return False, "服务器异常"
    except Exception as e:
        return False, str(e)


# ── 交互模式 ─────────────────────────────
def guide_get_cookie():
    print(f"""
╔══════════════════════════════════════════╗
║         获取 Cookie（30 秒搞定）          ║
╠══════════════════════════════════════════╣
║                                          ║
║  1. 浏览器打开 {BASE}          ║
║  2. 登录，勾选 Remember Me              ║
║  3. F12 → Console → 输入并回车:          ║
║     copy(document.cookie)                ║
║  4. Cookie 已复制到剪贴板               ║
║                                          ║
╚══════════════════════════════════════════╝
""")
    # 尝试从剪贴板读取
    cookie_str = ""
    try:
        import subprocess
        result = subprocess.run(
            ['powershell', '-Command', 'Get-Clipboard'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0 and 'uid=' in result.stdout and 'key=' in result.stdout:
            cookie_str = result.stdout.strip()
            print(f"  检测到剪贴板内容 ({len(cookie_str)} 字符)，自动使用。")
            print(f"  {cookie_str[:80]}...")
            choice = input("
  确认使用？[Y/n] ").strip().lower()
            if choice == 'n':
                cookie_str = ""
    except Exception:
        pass

    # 剪贴板读取失败或用户拒绝，手动粘贴
    if not cookie_str:
        print("  请将 Cookie 粘贴到此处（右键 → 粘贴，然后回车）:")
        print("  > ", end="")
        cookie_str = input().strip()

    # 保存
    if cookie_str:
        with open(COOKIE_FILE, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        print(f"  ✅ Cookie 已保存 ({len(cookie_str)} 字符)")
    else:
        print("  ❌ 未检测到有效内容")


def run_interactive(log):
    print(f"""
  ╔══════════════════════════════╗
  ║   ikuuu.win 每日签到        ║
  ╚══════════════════════════════╝""")

    status, desc = cookie_status()
    icon = {"ok": "✅", "expired": "❌", "missing": "❌", "invalid": "⚠️", "unknown": "⚠️"}
    print(f"  Cookie: {icon.get(status, '?')} {desc}")

    if status != "ok":
        print("\n  需要先获取有效的 Cookie。")
        guide_get_cookie()
        status, desc = cookie_status()
        if status != "ok":
            print(f"\n  Cookie 仍然无效 ({desc})，请检查后重试。")
            input("\n按回车退出...")
            return

    print("\n  签到中...")
    success, msg = do_checkin()

    if success:
        print(f"  ✅ {msg}")
    else:
        print(f"  ❌ {msg}")
        if "失效" in msg:
            print("\n  重新获取 Cookie...")
            guide_get_cookie()
            success, msg = do_checkin()
            print(f"  {'✅' if success else '❌'} {msg}")

    print()
    input("按回车退出...")


# ── 静默模式 ─────────────────────────────
def run_silent(log):
    status, desc = cookie_status()
    if status != "ok":
        log.error(f"Cookie {desc}，签到中止")
        sys.exit(1)

    success, msg = do_checkin()
    if success:
        log.info(f"OK - {msg}")
    else:
        log.error(f"FAIL - {msg}")
        sys.exit(1)


# ── 入口 ─────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--silent', action='store_true', help='静默模式（仅写日志，不弹窗）')
    args = parser.parse_args()

    log = setup_logging(args.silent)

    try:
        if args.silent:
            run_silent(log)
        else:
            run_interactive(log)
    except KeyboardInterrupt:
        if not args.silent:
            print("\n已取消")
    except Exception as e:
        log.error(f"异常: {e}")
        if not args.silent:
            input("\n按回车退出...")
        sys.exit(1)
