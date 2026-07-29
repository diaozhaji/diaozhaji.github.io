#!/usr/bin/env python3
"""博客文章生成器 — 创建新文章并自动更新 posts.json

用法:
  python3 new_post.py                # 交互模式（逐行输入正文）
  python3 new_post.py --md post.md   # 从 Markdown 文件生成
  python3 new_post.py --md post.md -t "标题" -s "摘要" --tags tag1,tag2  # 全自动
"""
import json, os, sys, re, argparse
from datetime import date

POSTS_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(POSTS_DIR, "posts", "posts.json")
POSTS_SUBDIR = os.path.join(POSTS_DIR, "posts")


def slugify(title):
    s = title.lower().replace(" ", "-")
    s = re.sub(r'[^\w\u4e00-\u9fff-]', '', s)
    return s


def md_to_html(text):
    """将 Markdown 文本转换为博客可用的 HTML。"""
    import markdown as md_lib
    import xml.etree.ElementTree as ET

    # 先用 fenced_code 解析代码块，其余用标准扩展
    body = md_lib.markdown(
        text,
        extensions=[
            'fenced_code',
            'codehilite',
            'tables',
            'footnotes',
        ],
        output_format='html5',
    )

    # 移除最外层的 <p> 包裹（markdown 把整段当段落）
    # 但实际上 markdown 生成的 HTML 是 <p> 包裹的段落，保留即可
    return body


def extract_title_from_md(text):
    """从 Markdown 中提取第一个 # 标题作为文章标题。"""
    for line in text.splitlines():
        line = line.strip()
        if line.startswith('# ') and not line.startswith('## '):
            return line[2:].strip()
    return None


def create_post_html(slug, title, date_str, tags, body_html):
    """生成完整的文章 HTML 页面。"""
    tag_badges = " · ".join(tags)
    return f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · diaozhaji的博客</title>
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  <header>
    <div class="header-inner">
      <a href="/" class="logo">diaozhaji<span>.</span></a>
      <nav>
        <a href="/">首页</a>
        <a href="../about.html">关于</a>
      </nav>
    </div>
  </header>

  <main class="container">
    <article>
      <div class="post-header">
        <h1>{title}</h1>
        <div class="post-meta">📅 {date_str} &nbsp;·&nbsp; 🏷️ {tag_badges}</div>
      </div>
      <div class="post-content">
{body_html}
      </div>
    </article>
  </main>

  <footer>
    <p>© 2026 diaozhaji的博客 · 用 ❤️ 和 AI 创作</p>
  </footer>
</body>
</html>
'''


def main():
    parser = argparse.ArgumentParser(description='创建博客文章')
    parser.add_argument('--md', metavar='FILE', help='Markdown 源文件路径')
    parser.add_argument('-t', '--title', help='文章标题（配合 --md 使用）')
    parser.add_argument('-s', '--summary', help='文章摘要')
    parser.add_argument('--tags', help='标签，逗号分隔')
    args = parser.parse_args()

    # ── 从 Markdown 文件生成 ──
    if args.md:
        md_path = args.md
        if not os.path.exists(md_path):
            print(f"❌ 找不到文件: {md_path}")
            sys.exit(1)

        with open(md_path, 'r', encoding='utf-8') as f:
            md_text = f.read()

        # 标题：优先命令行参数，其次从 Markdown 提取
        title = args.title or extract_title_from_md(md_text)
        if not title:
            title = input("📝 文章标题: ").strip()
        if not title:
            print("❌ 标题不能为空")
            sys.exit(1)

        slug = slugify(title)
        today = date.today().isoformat()

        # 摘要和标签
        summary = args.summary
        if not summary:
            summary = input("📋 摘要（一句话）: ").strip()

        tags_input = args.tags
        if not tags_input:
            tags_input = input("🏷️ 标签（逗号分隔）: ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        # 移除 Markdown 中标题行（避免正文重复显示标题）
        md_body = md_text
        lines = md_text.splitlines()
        for i, line in enumerate(lines):
            if line.strip().startswith('# ') and not line.strip().startswith('## '):
                md_body = '\n'.join(lines[i+1:]).strip()
                break

        body_html = md_to_html(md_body)

    # ── 交互模式 ──
    else:
        title = input("📝 文章标题: ").strip()
        if not title:
            print("❌ 标题不能为空")
            return

        slug = slugify(title)
        today = date.today().isoformat()
        summary = input("📋 摘要（一句话）: ").strip()
        tags_input = input("🏷️ 标签（逗号分隔）: ").strip()
        tags = [t.strip() for t in tags_input.split(",") if t.strip()]

        print("✍️ 输入正文内容（空行+Ctrl+D 结束）:")
        lines = sys.stdin.read().strip().split("\n") if not sys.stdin.isatty() else []

        if not lines:
            body_html = "      <p>正在撰写中，敬请期待...</p>"
        else:
            body_parts = []
            for line in lines:
                body_parts.append(f"      <p>{line}</p>")
            body_html = "\n".join(body_parts)

    # ── 读已有文章清单 ──
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            posts = json.load(f)
    else:
        posts = []

    # ── 生成完整 HTML ──
    html = create_post_html(slug, title, today, tags, body_html)

    # ── 写入 HTML ──
    os.makedirs(POSTS_SUBDIR, exist_ok=True)
    post_path = os.path.join(POSTS_SUBDIR, f"{slug}.html")
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 文章已创建: posts/{slug}.html")

    # ── 更新清单 ──
    # 避免 slug 重复
    existing = [p for p in posts if p["slug"] != slug]
    existing.append({
        "slug": slug,
        "title": title,
        "date": today,
        "summary": summary,
        "tags": tags
    })
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    print(f"✅ 文章清单已更新")


if __name__ == "__main__":
    main()
