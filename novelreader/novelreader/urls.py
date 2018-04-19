"""novelreader URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.conf import settings
from django.contrib import admin
from .views import (
    IndexView,
    NovelView,
    ChapterView,
    ProfileView,
    StatView,
    CategoryView,
    SearchView,
    TopView,
)
from .views.test import TestView


def t(name):
    return 'novelreader/' + name


urlpatterns = [
    url(r'^_admin_/', admin.site.urls),

    url(r'^$', IndexView.as_view(template_name=t('index.html')), name='index'),
    url(r'^(?P<nid>\d+)/$', NovelView.as_view(template_name=t('novel.html')), name='novel'),
    url(r'^(?P<nid>\d+)/(?P<cid>\d+)/$', ChapterView.as_view(template_name=t('chapter.html')), name='chapter'),
    url(r'^category/(?P<category>[^/]+)/$', CategoryView.as_view(template_name=t('category.html')), name='category'),
    url(r'^top/(?P<top>[^/]+)/$', TopView.as_view(template_name=t('top.html')), name='top'),
    url(r'^profile/$', ProfileView.as_view(template_name=t('profile.html')), name='profile'),
    url(r'^search/$', SearchView.as_view(template_name=t('search.html')), name='search'),

    url(r'^stat/$', StatView.as_view(), name='stat') if settings else None,

    url(r"^test/(?P<name>\w+)/$", TestView.as_view()),

    url(r'^accounts/', include('allauth.urls')),

]   # + static(settings.STATIC_URL + 'albums/', document_root=settings.STATICFILES_DIRS[1])


# for silk profiling
try:
    urlpatterns += [url(r'^_silk_/', include('silk.urls', namespace='silk'))]
except:
    pass