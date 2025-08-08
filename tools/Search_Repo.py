#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Search Spider – Star-History 图表版
-------------------------------------------------
把常用的“搜索限制 / 输出格式”全部提到文件头部常量区，方便一键改配置。
支持命令行参数：
    --query        必须（--update 时除外），搜索关键字（如 python）
    --output       可选，保存结果的 markdown 文件名
    --max-items    可选，最多返回多少条（默认 100）
    --min-stars    可选，最低 star 数（默认 5000）
    --max-desc     可选，描述最长字符数（默认 1000）
    --update       可选，与 -o 共用，重新生成该文件
"""

import sys
import argparse
import textwrap
import requests
import re
from datetime import datetime
from typing import List, Dict

# ------------------------------------------------------------------
# 1. 可配置常量区
# ------------------------------------------------------------------
GITHUB_API_URL = "https://api.github.com/search/repositories"
SORT_BY = "stars"
ORDER_BY = "desc"

DEFAULT_MAX_ITEMS = 100
DEFAULT_MIN_STARS = 5000
DEFAULT_MAX_DESC = 1000

MARKDOWN_HEADER = textwrap.dedent("""\
    |Stars|Repository|Description|Language|Updated|Created|
    |:-|:-|:-|:-|:-|:-|
""")

# ------------------------------------------------------------------
# 2. 命令行解析
# ------------------------------------------------------------------
parser = argparse.ArgumentParser(
    description="Search trending repositories on GitHub and export to markdown with Star-History chart.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter
)

parser.add_argument("-q", "--query",
                    help="Search keyword(s). Same syntax as GitHub web search.")
parser.add_argument("-o", "--output",
                    help="Output markdown file. If omitted, only print to stdout.")
parser.add_argument("--max-items", type=int, default=DEFAULT_MAX_ITEMS,
                    help="Maximum number of repositories to return.")
parser.add_argument("--min-stars", type=int, default=DEFAULT_MIN_STARS,
                    help="Minimum number of stars to include.")
parser.add_argument("--max-desc", type=int, default=DEFAULT_MAX_DESC,
                    help="Maximum length of description before truncation.")
parser.add_argument("--update", action="store_true",
                    help="Re-generate the markdown file specified by -o. "
                         "When this flag is used, -q/--query is ignored and other "
                         "parameters are read from the existing file header.")

args = parser.parse_args()

# ------------------------------------------------------------------
# 3. 处理 --update 场景
# ------------------------------------------------------------------
if args.update:
    if not args.output:
        sys.exit("ERROR: --update must be used together with -o/--output")
    try:
        with open(args.output, "r", encoding="utf-8") as f:
            content = f.read()
    except FileNotFoundError:
        sys.exit(f"ERROR: {args.output} not found. Cannot perform --update.")

    # 从头文件解析原始 query
    m = re.search(r"^#+\s+Query:\s*(.+)$", content, flags=re.MULTILINE)
    if not m:
        sys.exit("ERROR: cannot extract original query from file header")
    original_query = m.group(1).strip()
    args.query = original_query  # 覆盖 query

    # 解析其他参数（简单正则，够用即可）
    def extract_param(name: str, type_func=int, default=None):
        p = re.search(rf"^\*\s*{name}:\s*(\S+)", content, flags=re.MULTILINE)
        return type_func(p.group(1)) if p else default

    args.max_items = extract_param("max-items", int, DEFAULT_MAX_ITEMS)
    args.min_stars = extract_param("min-stars", int, DEFAULT_MIN_STARS)
    args.max_desc = extract_param("max-desc", int, DEFAULT_MAX_DESC)

if not args.query:
    sys.exit("ERROR: --query is required when --update is not used")

if args.max_items <= 0:
    sys.exit("ERROR: --max-items must be a positive integer")
if args.min_stars < 0:
    sys.exit("ERROR: --min-stars must be non-negative")
if args.max_desc < 0:
    sys.exit("ERROR: --max-desc must be non-negative")

# ------------------------------------------------------------------
# 4. 网络请求
# ------------------------------------------------------------------
url = f"{GITHUB_API_URL}?q={args.query}&sort={SORT_BY}&order={ORDER_BY}"
print(f"Requesting: {url}", file=sys.stderr)
resp = requests.get(url, timeout=30)

if resp.status_code != 200:
    sys.exit(f"GitHub API error: {resp.status_code}\n{resp.text}")

data = resp.json()
total = data.get("total_count", 0)
items: List[Dict] = data.get("items", [])
print(f"Total repositories found: {total}", file=sys.stderr)

# ------------------------------------------------------------------
# 5. 过滤
# ------------------------------------------------------------------
def make_md_line(repo: Dict) -> str:
    name = repo["full_name"]
    url = repo["html_url"]
    stars = repo["stargazers_count"]
    lang = repo["language"] or "/"
    updated = repo["updated_at"][:10]
    created = repo["created_at"][:10]

    desc = repo["description"] or "/"
    if len(desc) > args.max_desc:
        desc = desc[: args.max_desc - 3] + "..."
    desc = desc.replace("|", "&#124;")

    return f"|{stars}|[{name}]({url})|{desc}|{lang}|{updated}|{created}|"

filtered = []
for repo in items:
    if len(filtered) >= args.max_items:
        break
    if repo["stargazers_count"] < args.min_stars:
        continue
    filtered.append(repo)

if not filtered:
    sys.exit("No repositories match the criteria.")

repo_names = [r["full_name"] for r in filtered[:10]]
lines = [make_md_line(r) for r in filtered]

# ------------------------------------------------------------------
# 6. 组装最终 markdown
# ------------------------------------------------------------------
chart_url = (
    "https://api.star-history.com/svg?repos="
    + ",".join(repo_names)
    + "&type=Date"
)
chart_md = (
    f"[![Star History Chart]({chart_url})]"
    f"(https://www.star-history.com/#{','.join(repo_names)}&Date)\n\n"
)

toc = textwrap.dedent("""\
    ## Table of Contents
    - [Star History Chart](#star-history-chart)
    - [Repository List](#repository-list)

""")

command_line = " ".join(sys.argv)

header = f"# Query: {args.query}\n\n" \
         f"* max-items: {args.max_items}\n" \
         f"* min-stars: {args.min_stars}\n" \
 f"* max-desc: {args.max_desc}\n\n" \
         f"```bash\n{command_line}\n```\n\n"

final_md = header + toc + "### Star History Chart\n\n" + chart_md + \
           "### Repository List\n\n" + MARKDOWN_HEADER + "\n".join(lines) + "\n"

# ------------------------------------------------------------------
# 7. 输出
# ------------------------------------------------------------------
if args.output:
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(final_md)
    action = "Updated" if args.update else "Created"
    print(f"{action} {args.output} with {len(lines)} rows.", file=sys.stderr)
else:
    print(final_md)