#!/usr/bin/env python3
"""
ikuuu.win 每日签到
====================
  ikuuu_sign.py          交互模式（默认），Cookie 过期自动引导
  ikuuu_sign.py -s       静默模式，仅签到写日志（供定时任务）
  ikuuu_sign.py --fetch  从主域名自动获取当前可用域名

主域名不可用时自动检测可用域名：
  ikuuu.one → ikuuu.win → ikuuu.co → ...
"""

import os, sys, json, time, logging, argparse
from urllib.parse import urlparse, unquote
import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__)) if not getattr(sys, 'frozen', False) else os.path.dirname(sys.executable)
os.chdir(SCRIPT_DIR)

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.json")

# ikuuu 所有已知域名，用于自动探测
IKUUU_DOMAINS = [
    "ikuuu.one", "ikuuu.win", "ikuuu.co", "ikuuu.ltd", "ikuuu.org",
    "ikuuu.live", "ikuuu.dev", "ikuuu.eu", "ikuuu.uk", "ikuuu.art",
    "ikuuu.boo", "ikuuu.fyi", "ikuuu.me", "ikuuu.pw", "ikuuu.top",
    "ikuuu.de", "ikuuu.nl", "ikuuu.ch",
]

# ── 日志 ──────────────────────────────────
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


# ── 配置 ──────────────────────────────────
def load_config():
    cfg = {
        "master_url": "https://ikuuu.one",
        "base_url": "https://ikuuu.win",
        "cookie_file": os.path.join(SCRIPT_DIR, "ikuuu_cookies.txt")
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            if 'site' in data:
                if 'master_url' in data['site']:
                    cfg['master_url'] = data['site']['master_url']
                if 'base_url' in data['site']:
                    cfg['base_url'] = data['site']['base_url']
            if 'cookie' in data and 'file' in data['cookie']:
                p = data['cookie']['file']
                cfg['cookie_file'] = p if os.path.isabs(p) else os.path.join(SCRIPT_DIR, p)
        except:
            pass
    return cfg


def save_config_base_url(url):
    """持久化当前可用域名"""
    try:
        cfg = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                cfg = json.load(f)
        cfg.setdefault('site', {})['base_url'] = url
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(cfg, f, indent=4, ensure_ascii=False)
    except:
        pass


# ── 域名探测 ──────────────────────────────
def probe_domain(url, timeout=5):
    """检测域名是否可达"""
    try:
        r = requests.get(url, timeout=timeout, allow_redirects=True)
        final = r.url.rstrip('/')
        host = urlparse(final).netloc
        # 确认是否仍为 ikuuu 域名
        if 'ikuuu' in host:
            return final
    except:
        pass
    return None


def resolve_active_domain(cfg, force=False):
    """
    从主域名获取当前生效域名。
    优先级: 主域名 -> 当前 base_url -> 遍历已知域名
    """
    # 1. 尝试主域名
    final = probe_domain(cfg['master_url'])
    if final and final != cfg['base_url']:
        return final

    # 2. 尝试当前 base_url（不强制时不重复探测）
    if not force:
        final = probe_domain(cfg['base_url'])
        if final:
            return final

    # 3. 遍历所有已知域名
    for domain in IKUUU_DOMAINS:
        url = f"https://{domain}"
        if url == cfg['base_url'] or url == cfg['master_url']:
            continue
        final = probe_domain(url, timeout=3)
        if final:
            return final

    # 全部失败，返回当前配置
    return cfg['base_url']


# ── Cookie ────────────────────────────────
def read_cookies(cookie_file):
    if not os.path.exists(cookie_file):
        return {}, ""
    with open(cookie_file, 'r', encoding='utf-8') as f:
        raw = f.read().strip()
    cookies = {}
    for item in raw.split(';'):
        item = item.strip()
        if '=' in item:
            k, v = item.split('=', 1)
            if v.strip():
                cookies[k.strip()] = v.strip()
    return cookies, raw


def cookie_status(cookie_file, base_url):
    cookies, _ = read_cookies(cookie_file)
    if not cookies:
        return "missing", "未获取"
    if 'uid' not in cookies or 'key' not in cookies:
        return "invalid", "内容不完整"
    try:
        s = requests.Session()
        s.headers['User-Agent'] = UA
        for k, v in cookies.items():
            s.cookies.set(k, v)
        r = s.get(f"{base_url}/user", timeout=8, allow_redirects=False)
        if r.status_code == 200:
            mtime = os.path.getmtime(cookie_file)
            hours = (time.time() - mtime) / 3600
            return "ok", f"有效 · {hours:.0f}h前"
        return "expired", "已过期"
    except:
        return "unknown", "无法验证"


# ── 签到 ──────────────────────────────────
def do_checkin(cookie_file, base_url):
    cookies, _ = read_cookies(cookie_file)
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
        s.get(f"{base_url}/user", timeout=10)
        r = s.post(f"{base_url}/user/checkin", timeout=10, headers={
            'Referer': f"{base_url}/user",
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


# ── Cookie 输入 ───────────────────────────
def guide_get_cookie(cookie_file, base_url):
    print(f"""
╔══════════════════════════════════════════╗
║         获取 Cookie（30 秒搞定）          ║
╠══════════════════════════════════════════╣
║  1. 浏览器打开 {base_url}          ║
║  2. 登录，勾选 Remember Me              ║
║  3. F12 → Console → 输入并回车:          ║
║     copy(document.cookie)                ║
║  4. 回终端，右键粘贴 → 回车              ║
╚══════════════════════════════════════════╝
""")
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
            if input("\n  确认使用？[Y/n] ").strip().lower() == 'n':
                cookie_str = ""
    except:
        pass

    if not cookie_str:
        print("  请粘贴 Cookie（右键 → 粘贴，回车）:")
        print("  > ", end="")
        cookie_str = input().strip()

    if cookie_str:
        with open(cookie_file, 'w', encoding='utf-8') as f:
            f.write(cookie_str)
        print(f"  ✅ Cookie 已保存 ({len(cookie_str)} 字符)")
    else:
        print("  ❌ 未检测到有效内容")


# ── 主流程 ────────────────────────────────
def run_interactive(log, cfg, base_url, cookie_file):
    print(f"""
  ╔══════════════════════════════╗
  ║   ikuuu.win 每日签到        ║
  ║   {urlparse(base_url).netloc:<24s} ║
  ╚══════════════════════════════╝""")

    status, desc = cookie_status(cookie_file, base_url)
    icon = {"ok": "✅", "expired": "❌", "missing": "❌", "invalid": "⚠️", "unknown": "⚠️"}
    print(f"  Cookie: {icon.get(status, '?')} {desc}")

    if status != "ok":
        print("\n  需要先获取有效的 Cookie。")
        guide_get_cookie(cookie_file, base_url)
        status, desc = cookie_status(cookie_file, base_url)
        if status != "ok":
            print(f"\n  Cookie 仍然无效 ({desc})，请检查后重试。")
            input("\n按回车退出...")
            return

    print("\n  签到中...")
    success, msg = do_checkin(cookie_file, base_url)

    if success:
        print(f"  ✅ {msg}")
    else:
        print(f"  ❌ {msg}")
        if "失效" in msg:
            print("\n  重新获取 Cookie...")
            guide_get_cookie(cookie_file, base_url)
            success, msg = do_checkin(cookie_file, base_url)
            print(f"  {'✅' if success else '❌'} {msg}")

    print()
    input("按回车退出...")


def run_silent(log, cfg, base_url, cookie_file):
    status, desc = cookie_status(cookie_file, base_url)
    if status != "ok":
        log.error(f"Cookie {desc}")
        sys.exit(1)

    success, msg = do_checkin(cookie_file, base_url)
    if success:
        log.info(f"OK - {msg}")
    else:
        log.error(f"FAIL - {msg}")
        sys.exit(1)


# ── 入口 ──────────────────────────────────
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-s', '--silent', action='store_true', help='静默模式')
    parser.add_argument('--fetch', action='store_true', help='强制重新探测可用域名')
    args = parser.parse_args()

    log = setup_logging(args.silent)
    cfg = load_config()

    # 探测可用域名
    base_url = resolve_active_domain(cfg, force=args.fetch)
    if base_url != cfg['base_url']:
        log.info(f"域名已切换: {urlparse(cfg['base_url']).netloc} → {urlparse(base_url).netloc}")
        save_config_base_url(base_url)

    cookie_file = cfg['cookie_file']

    try:
        if args.silent:
            run_silent(log, cfg, base_url, cookie_file)
        else:
            run_interactive(log, cfg, base_url, cookie_file)
    except KeyboardInterrupt:
        if not args.silent:
            print("\n已取消")
    except Exception as e:
        log.error(f"异常: {e}")
        if not args.silent:
            input("\n按回车退出...")
        sys.exit(1)
