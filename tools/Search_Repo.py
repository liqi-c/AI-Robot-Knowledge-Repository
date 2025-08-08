#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Search Spider – “三阶段更新”实现
-------------------------------------------------
--update 时逻辑：
  1. 解析旧 .md 文件 → 当前保留条目（current）
  2. 解析 .cache.json → 历史全部条目（cache）
  3. 重新搜索 → 最新条目（latest）
  4. 合并规则：
     - 若 latest 在 cache 中但不在 current → 用户删过，跳过
     - 若 latest 不在 cache → 新增，写入 current 和 cache
     - 若 latest 在 cache 也在 current → 更新内容
  5. 重写 .md 和 .cache.json
"""

import sys
import argparse
import json
import re
import requests
import os
from typing import List, Dict

GITHUB_API_URL = "https://api.github.com/search/repositories"
SORT_BY = "stars"
ORDER_BY = "desc"
MARKDOWN_HEADER = "|Stars|Repository|Description|Language|Updated|Created|\n|:-|:-|:-|:-|:-|:-|\n"

# ---------- 工具 ----------
def search_repos(query: str, max_items: int, min_stars: int) -> List[Dict]:
    url = f"{GITHUB_API_URL}?q={query}+stars:>={min_stars}&sort={SORT_BY}&order={ORDER_BY}"
    print(f"API: {url}", file=sys.stderr)
    resp = requests.get(url, timeout=30)
    if resp.status_code != 200:
        sys.exit(f"API error {resp.status_code}: {resp.text}")
    return resp.json().get("items", [])[:max_items]

def make_line(repo: Dict, max_desc: int) -> str:
    name = repo["full_name"]
    url = repo["html_url"]
    stars = repo["stargazers_count"]
    lang = repo["language"] or "/"
    updated = repo["updated_at"][:10]
    created = repo["created_at"][:10]
    desc = (repo["description"] or "/")[:max_desc].replace("|", "&#124;")
    return f"|{stars}|[{name}]({url})|{desc}|{lang}|{updated}|{created}|"

# ---------- 解析旧文件 ----------
def parse_md(path: str) -> Dict[str, Dict]:
    """返回 {full_name: repo_dict}"""
    if not os.path.isfile(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        text = f.read()
    lines = [ln for ln in text.splitlines() if ln.startswith("|") and "](" in ln and "Repository" not in ln]
    current = {}
    for ln in lines:
        m = re.search(r"\[([^]]+)\]", ln)
        if not m:
            continue
        key = m.group(1)
        # 为了简单，只存 key；后续用 latest 的 repo_dict 更新
        current[key] = {}
    return current

# ---------- 主流程 ----------
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-q", "--query", help="Search keyword(s)")
    parser.add_argument("-o", "--output", required=True, help="Output markdown file")
    parser.add_argument("--max-items", type=int, default=100)
    parser.add_argument("--min-stars", type=int, default=1000)
    parser.add_argument("--max-desc", type=int, default=1000)
    parser.add_argument("--update", action="store_true", help="Update existing file")
    args = parser.parse_args()

    cache_dir = os.path.join(os.path.dirname(args.output), ".cache")
    os.makedirs(cache_dir, exist_ok=True)
    cache_file = os.path.join(cache_dir, f".{os.path.basename(args.output).rsplit('.', 1)[0]}.json")
    
    # 1. 解析旧文件
    current_md = parse_md(args.output)              # 当前 md 中存在的条目
    cache_data = {}                                 # 历史全部条目
    if os.path.isfile(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            cache_data = json.load(f)

    # 2. 重新搜索
    if args.update:
        # 从旧 md 头部读取参数
        with open(args.output, "r", encoding="utf-8") as f:
            head = f.read()
        m = re.search(r"Query:\s*(.+)", head)
        if not m:
            sys.exit("Cannot read original query from .md header")
        query = m.group(1).strip()
    else:
        if not args.query:
            sys.exit("Need --query")
        query = args.query

    latest_list = search_repos(query, args.max_items, args.min_stars)
    latest_map = {r["full_name"]: r for r in latest_list}

    # 3. 合并
    updated_cache = cache_data.copy()
    updated_md_lines = []

    for key, repo in latest_map.items():
        if key in cache_data and key not in current_md:
            # 用户删过，跳过
            continue
        updated_cache[key] = repo
        updated_md_lines.append(make_line(repo, args.max_desc))

    # 4. 排序
    updated_md_lines.sort(key=lambda ln: int(ln.split("|")[1]), reverse=True)

    # 5. 写回
    repo_names = list(latest_map.keys())[:10]
    chart_url = f"https://api.star-history.com/svg?repos={','.join(repo_names)}&type=Date"
    chart_link = f"https://www.star-history.com/#{','.join(repo_names)}&Date"

    md_table = '\n'.join(updated_md_lines)

    body = (
        f"# Query: {query}\n\n"
        f"* max-items: {args.max_items}\n"
        f"* min-stars: {args.min_stars}\n"
        f"* max-desc: {args.max_desc}\n\n"
        f"```bash\n{' '.join(sys.argv)}\n```\n\n"
        f"## Table of Contents\n"
        f"- [Star History Chart](#star-history-chart)\n"
        f"- [Repository List](#repository-list)\n\n"
        f"### Star History Chart\n\n"
        f"[![Star History Chart]({chart_url})]({chart_link})\n\n"
        f"### Repository List\n\n"
        f"{MARKDOWN_HEADER}"
        f"{md_table}\n"
    )
        
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(body)
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(updated_cache, f, indent=2, ensure_ascii=False)
    print(f"{'Updated' if args.update else 'Created'} {args.output} ({len(updated_md_lines)} rows)")

if __name__ == "__main__":
    main()