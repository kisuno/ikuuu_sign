"""
iKuuuVPN 轻量域名解析器 (纯 requests 版本)
==========================================
依赖: pip install requests
原理: 解码JS碎片 + 搜索JS字面量 → 双重覆盖

用法:
    python ikuuu_parser.py
"""

import re
import base64
import sys
import json

import requests


# ============================================================
#  核心解析逻辑
# ============================================================
def parse(url="https://ikuuu.one/"):
    """
    纯 requests 方案 —— 不需要浏览器
    通过两个维度提取 TLD:
      1. 解码 264 个 Base64 碎片 → 搜索 .xxx 模式
      2. 在原始 JS 中搜索字面量 '.xxx' 字符串
    """

    # ---- 自定义 Base64 编解码 ----
    CUSTOM_ALPH = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+/='
    STD_ALPH    = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/='

    def decode_fragment(encoded):
        """解码单个碎片"""
        std = ''
        for ch in encoded:
            idx = CUSTOM_ALPH.find(ch)
            if idx == -1:
                std += ch
            elif idx == 64:
                std += '='
            else:
                std += STD_ALPH[idx]
        rem = len(std) % 4
        if rem:
            std += '=' * (4 - rem)
        try:
            return base64.b64decode(std).decode('utf-8', errors='replace')
        except:
            return ''

    # ---- 1. 获取页面 ----
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    resp = requests.get(url, headers=headers, timeout=15)
    resp.encoding = 'utf-8'
    html = resp.text

    # ---- 2. 提取编码数组并解码 ----
    match = re.search(r"_0x4e73\(\)\{const _0x3c078b=\[(.*?)\];", html, re.DOTALL)
    if not match:
        return {'error': '无法找到编码数组', 'domains': []}

    items = re.findall(r"'([^']*)'", match.group(1))
    decoded = [decode_fragment(item) for item in items]

    # ---- 3. 从碎片中找 TLD ----
    fragment_tlds = set()
    for text in decoded:
        text = text.strip()
        m = re.match(r'^\.([a-z]{2,})$', text)
        if m:
            fragment_tlds.add('.' + m.group(1))

    # ---- 4. 从 JS 字面量中找 TLD ----
    scripts = re.findall(r'<script[^>]*>(.*?)</script>', html, re.DOTALL)
    js_source = scripts[0] if scripts else html

    literal_tlds = set()
    # 匹配 + '.xxx' 或单独的 '.xxx'
    for m in re.finditer(r"'(\.[a-z]{2,})'", js_source):
        literal_tlds.add(m.group(1))

    # ---- 5. 合并 TLD，生成域名 ----
    all_tlds = fragment_tlds | literal_tlds
    domains = []

    for tld in sorted(all_tlds):
        domain = 'ikuuu' + tld
        domains.append({
            'domain': domain,
            'url': f'https://{domain}/',
            'source': 'literal' if tld in literal_tlds else 'fragment'
        })

    # ---- 6. 提取标题 ----
    title_match = re.search(r'<title>(.*?)</title>', html, re.IGNORECASE)
    title = title_match.group(1) if title_match else '未知'

    return {
        'title': title,
        'domains': domains,
        'tlds_found': list(all_tlds),
        'method': 'pure requests'
    }


# ============================================================
def main():
    print("=" * 50)
    print("  iKuuuVPN 轻量域名解析器 (requests)")
    print("=" * 50)

    try:
        result = parse()
    except Exception as e:
        print(f"\n❌ 解析失败: {e}")
        sys.exit(1)

    if not result.get('domains'):
        print("\n⚠️ 未发现域名")
        sys.exit(0)

    print(f"\n📌 页面: {result['title']}")
    print(f"🔧 方式: {result['method']}")
    print(f"🔑 发现的 TLD: {result['tlds_found']}")
    print(f"\n{'='*40}")
    print(f"  可用域名列表:")
    print(f"{'='*40}")

    for i, d in enumerate(result['domains'], 1):
        print(f"  {i}. 🟢 {d['domain']}")
        print(f"     → {d['url']}  (来源: {d['source']})")
        print()

    print(f"  共 {len(result['domains'])} 个域名")

    # 输出 JSON（方便程序化调用）
    if '--json' in sys.argv:
        print("\n--- JSON ---")
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
