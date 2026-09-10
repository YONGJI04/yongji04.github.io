<div class="awards">
  {% for item in site.data.news.main %}
  <div class="award-row">
    <div class="award-content">
      <div class="award-title">{{ item.text }}</div>
      <div class="award-meta">{{ item.date }}</div>
    </div>
  </div>
  {% endfor %}
</div>
