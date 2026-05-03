#!/usr/bin/env python3
"""
ikuuu 每日签到
================
  ikuuu_sign.py          交互模式
  ikuuu_sign.py -s       静默模式（定时任务）

域名策略:
  默认 ikuuu.one（主站），不可达时轮询 domains 列表。
  脚本启动时自动探测可用域名并更新配置。
"""

import os, sys, json, logging, argparse
from urllib.parse import urlparse, unquote
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
os.chdir(SCRIPT_DIR)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# 内置域名池（ikuuu.one 不可达时轮询）
BUILTIN_DOMAINS = ["ikuuu.one", "ikuuu.win", "ikuuu.fyi"]


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


def load_config():
    cfg = {"base_url": "https://ikuuu.one", "cookie": "", "domains": list(BUILTIN_DOMAINS)}
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'site' in data and 'base_url' in data['site']:
                cfg['base_url'] = data['site']['base_url']
            if 'cookie' in data:
                cfg['cookie'] = data['cookie']
            if 'domains' in data:
                cfg['domains'] = data['domains']
        except:
            pass
    return cfg


def save_config(cfg):
    with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
        json.dump({
            "site": {"base_url": cfg['base_url']},
            "cookie": cfg['cookie'],
            "domains": cfg['domains']
        }, f, indent=4, ensure_ascii=False)


# ── 域名探测 ──────────────────────────────
def probe(domain):
    """检测域名是否可达"""
    try:
        r = requests.get(f"https://{domain}/auth/login", timeout=5,
                        headers={'User-Agent': UA})
        return r.status_code == 200
    except:
        return False


def resolve_domain(cfg):
    """返回当前可用域名"""
    # 1. 当前域名
    current = urlparse(cfg['base_url']).netloc
    if probe(current):
        return cfg['base_url']

    # 2. 轮询域名池
    for d in cfg['domains']:
        url = f"https://{d}"
        if d != current and probe(d):
            return url

    # 3. 轮询内置兜底
    for d in BUILTIN_DOMAINS:
        url = f"https://{d}"
        if d != current and probe(d):
            return url

    return cfg['base_url']


# ── Cookie ────────────────────────────────
def parse_cookies(cookie_str):
    cookies = {}
    for item in cookie_str.split(';'):
        item = item.strip()
        if '=' in item:
            k, v = item.split('=', 1)
            if v.strip():
                cookies[k.strip()] = v.strip()
    return cookies


def cookie_valid(cfg):
    cookies = parse_cookies(cfg['cookie'])
    if not cookies or 'uid' not in cookies or 'key' not in cookies:
        return "missing"
    try:
        s = requests.Session()
        s.headers['User-Agent'] = UA
        for k, v in cookies.items():
            s.cookies.set(k, v)
        r = s.get(f"{cfg['base_url']}/user", timeout=8, allow_redirects=False)
        return "ok" if r.status_code == 200 else "expired"
    except:
        return "unknown"


def do_checkin(cfg):
    cookies = parse_cookies(cfg['cookie'])
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
        s.get(f"{cfg['base_url']}/user", timeout=10)
        r = s.post(f"{cfg['base_url']}/user/checkin", timeout=10, headers={
            'Referer': f"{cfg['base_url']}/user",
            'X-Requested-With': 'XMLHttpRequest',
        })
        data = r.json()
        ret = data.get('ret', -1)
        msg = data.get('msg', str(data))
        return (True, msg) if ret == 1 else (True, msg)
    except requests.exceptions.JSONDecodeError:
        return False, "Cookie 已失效" if 'login' in r.text.lower() else "服务器异常"
    except Exception as e:
        return False, str(e)


def guide_get_cookie(cfg):
    print(f"""
╔══════════════════════════════════════════╗
║         获取 Cookie（30 秒搞定）          ║
╠══════════════════════════════════════════╣
║  1. 浏览器打开 {cfg['base_url']}          ║
║  2. 登录，勾选 Remember Me              ║
║  3. F12 → Console → 输入并回车:          ║
║     copy(document.cookie)                ║
║  4. 回终端，右键粘贴 → 回车              ║
╚══════════════════════════════════════════╝
""")
    cookie_str = ""
    try:
        import subprocess
        r = subprocess.run(['powershell', '-Command', 'Get-Clipboard'],
                          capture_output=True, text=True, timeout=5)
        if r.returncode == 0 and 'uid=' in r.stdout and 'key=' in r.stdout:
            cookie_str = r.stdout.strip()
            print(f"  剪贴板检测到 Cookie ({len(cookie_str)} 字符)")
            print(f"  {cookie_str[:80]}...")
            if input("\n  确认使用？[Y/n] ").strip().lower() == 'n':
                cookie_str = ""
    except:
        pass

    if not cookie_str:
        print("  请粘贴 Cookie（右键 → 粘贴，回车）:")
        print("  > ", end="")
        cookie_str = input().strip()

    if cookie_str:
        cfg['cookie'] = cookie_str
        save_config(cfg)
        print(f"  ✅ Cookie 已写入 config.json")
    else:
        print("  ❌ 未检测到有效内容")


def run(log, cfg, silent):
    # 域名
    url = resolve_domain(cfg)
    if url != cfg['base_url']:
        log.info(f"域名: {urlparse(cfg['base_url']).netloc} → {urlparse(url).netloc}")
        cfg['base_url'] = url
        save_config(cfg)

    domain = urlparse(cfg['base_url']).netloc

    if silent:
        status = cookie_valid(cfg)
        if status != "ok":
            log.error(f"Cookie {status}")
            sys.exit(1)
        success, msg = do_checkin(cfg)
        log.info(f"OK - {msg}" if success else f"FAIL - {msg}")
        sys.exit(0 if success else 1)

    # 交互模式
    status = cookie_valid(cfg)
    icon = {"ok": "✅", "expired": "❌", "missing": "❌", "unknown": "⚠️"}

    print(f"""
  ╔══════════════════════════════╗
  ║   ikuuu 每日签到             ║
  ║   {domain:<24s} ║
  ║   Cookie: {icon.get(status, '?')} {status:<7s} ║
  ╚══════════════════════════════╝""")

    if status != "ok":
        print("\n  需要先获取有效的 Cookie。")
        guide_get_cookie(cfg)
        status = cookie_valid(cfg)
        if status != "ok":
            print(f"\n  Cookie 仍然无效，请检查后重试。")
            input("\n按回车退出...")
            return

    print("\n  签到中...")
    success, msg = do_checkin(cfg)
    print(f"  {'✅' if success else '❌'} {msg}")

    if not success and "失效" in msg:
        print("\n  重新获取 Cookie...")
        guide_get_cookie(cfg)
        success, msg = do_checkin(cfg)
        print(f"  {'✅' if success else '❌'} {msg}")

    print()
    input("按回车退出...")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--silent', action='store_true', help='静默模式')
    args = parser.parse_args()

    log = setup_logging(args.silent)
    cfg = load_config()

    try:
        run(log, cfg, args.silent)
    except KeyboardInterrupt:
        if not args.silent: print("\n已取消")
    except Exception as e:
        log.error(f"异常: {e}")
        if not args.silent: input("\n按回车退出...")
        sys.exit(1)
