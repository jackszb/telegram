#!/usr/bin/env python3
"""
从 Telegram 官方地址下载 CIDR 列表，排序后生成 telegramip.json
官方地址: https://core.telegram.org/resources/cidr.txt
"""

import ipaddress
import json
import sys
import urllib.request

SOURCE_URL = "https://core.telegram.org/resources/cidr.txt"
OUTPUT_FILE = "telegramip.json"


def fetch_cidr_list(url: str) -> list[str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8")

    lines = []
    for line in raw.splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        lines.append(line)
    return lines


def sort_key(cidr: str):
    """
    排序规则：先 IPv4 后 IPv6，同类型内按网络地址数值升序排列
    """
    network = ipaddress.ip_network(cidr, strict=False)
    version = network.version
    return (version, int(network.network_address), network.prefixlen)


def build_json(cidr_list: list[str]) -> dict:
    valid = []
    for cidr in cidr_list:
        try:
            ipaddress.ip_network(cidr, strict=False)
            valid.append(cidr)
        except ValueError:
            print(f"警告：忽略无法解析的条目: {cidr}", file=sys.stderr)

    valid.sort(key=sort_key)

    return {
        "version": 3,
        "rules": [
            {
                "ip_cidr": valid
            }
        ]
    }


def main():
    print(f"正在从 {SOURCE_URL} 下载 CIDR 列表...")
    cidr_list = fetch_cidr_list(SOURCE_URL)
    print(f"共获取到 {len(cidr_list)} 条记录")

    data = build_json(cidr_list)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print(f"已生成 {OUTPUT_FILE}，共 {len(data['rules'][0]['ip_cidr'])} 条 CIDR")


if __name__ == "__main__":
    main()
