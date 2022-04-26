# from django.shortcuts import render

# Импорт класса TemplateView, чтобы унаследоваться от него
from django.views.generic.base import TemplateView


class AboutAuthorView(TemplateView):
    # В переменной template_name обязательно указывается имя шаблона,
    # на основе которого будет создана возвращаемая страница
    template_name = 'about/author.html'


class AboutTechView(TemplateView):
    template_name = 'about/tech.html'
