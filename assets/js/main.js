// shxiacc的博客 — 文章加载
(async function() {
  const list = document.getElementById('postList');
  if (!list) return;

  try {
    const res = await fetch('posts/posts.json');
    const posts = await res.json();
    
    // 按日期倒序
    posts.sort((a, b) => b.date.localeCompare(a.date));

    posts.forEach(p => {
      const li = document.createElement('li');
      li.className = 'post-item';
      li.innerHTML = `
        <div class="post-date">${p.date}</div>
        <a href="posts/${p.slug}.html" class="post-title">${p.title}</a>
        <div class="post-summary">${p.summary}</div>
        <div class="post-tags">
          ${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}
        </div>
      `;
      list.appendChild(li);
    });
  } catch (e) {
    list.innerHTML = '<li class="post-item"><p>暂无文章，敬请期待 📝</p></li>';
  }
})();
