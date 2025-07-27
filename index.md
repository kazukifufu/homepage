---
layout: default
title: Table of Contents
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

[🌤 PythonでAccuWeather APIを使って時間別天気を自動取得してみた！](Projects/weather/How to gather weather related information daily?.md)

[天気情報の収集方法](./Projects/weather/How to gather weather related information daily.md)
