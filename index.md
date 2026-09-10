---
layout: homepage
---

## About Me

I am interested in 3D Computer Vision and Generative AI.

## News

{% if site.data.publications.main.size > 0 %}
{% include_relative _includes/publications.md %}
{% endif %}

{% include_relative _includes/experience.md %}

{% include_relative _includes/awards.md %}

{% if site.data.scholarships.main.size > 0 %}
{% include_relative _includes/scholarships.md %}
{% endif %}
