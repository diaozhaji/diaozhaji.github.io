#!/usr/bin/env python3
"""博客文章生成器 — 创建新文章并自动更新 posts.json"""
import json, os, sys
from datetime import date

POSTS_DIR = os.path.dirname(os.path.abspath(__file__))
MANIFEST = os.path.join(POSTS_DIR, "posts.json")

def slugify(title):
    import re
    s = title.lower().replace(" ", "-")
    s = re.sub(r'[^\w\u4e00-\u9fff-]', '', s)
    return s

def main():
    title = input("📝 文章标题: ").strip()
    if not title:
        print("❌ 标题不能为空")
        return

    slug = slugify(title)
    today = date.today().isoformat()
    summary = input("📋 摘要（一句话）: ").strip()
    tags_input = input("🏷️ 标签（逗号分隔）: ").strip()
    tags = [t.strip() for t in tags_input.split(",") if t.strip()]

    # 读已有文章清单
    if os.path.exists(MANIFEST):
        with open(MANIFEST, encoding="utf-8") as f:
            posts = json.load(f)
    else:
        posts = []

    # 生成文章HTML
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{title} · shxiacc的博客</title>
  <link rel="stylesheet" href="../assets/css/style.css">
</head>
<body>
  <header>
    <div class="header-inner">
      <a href="/" class="logo">shxiacc<span>.</span></a>
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
        <div class="post-meta">📅 {today} &nbsp;·&nbsp; 🏷️ {" · ".join(tags)}</div>
      </div>
'''
    
    print("✍️ 输入正文内容（空行+Ctrl+D 结束）:")
    lines = sys.stdin.read().strip().split("\n") if not sys.stdin.isatty() else []
    if not lines:
        print("  (正文留空，稍后手动编辑)")
        html += "      <p>正在撰写中，敬请期待...</p>\n"
    else:
        for line in lines:
            html += f"      <p>{line}</p>\n"

    html += '''    </article>
  </main>

  <footer>
    <p>© 2026 shxiacc的博客 · 用 ❤️ 和 AI 创作</p>
  </footer>
</body>
</html>
'''

    # 写入HTML
    post_path = os.path.join(POSTS_DIR, f"{slug}.html")
    with open(post_path, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"✅ 文章已创建: posts/{slug}.html")

    # 更新清单
    posts.append({
        "slug": slug,
        "title": title,
        "date": today,
        "summary": summary,
        "tags": tags
    })
    with open(MANIFEST, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=2)
    print(f"✅ 文章清单已更新")

if __name__ == "__main__":
    main()
