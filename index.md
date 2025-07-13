---
layout: default
title: ノート一覧
---

# 📚 ノート一覧

<ul>
  {% for post in site.posts %}
    <li>
      <a href="/homepage{{ post.url }}">{{ post.title }}</a>
      <div class="note-date">{{ post.date | date: "%Y年%-m月%-d日" }}</div>
    </li>
  {% endfor %}
</ul>
