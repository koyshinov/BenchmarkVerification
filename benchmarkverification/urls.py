"""benchmarkverification URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.urls import path, include

from run.views import run_page


urlpatterns = [
    path('admin/', admin.site.urls),
    url(r'^', include(('core.urls', 'core'), namespace="core")),
    url(r'^run$', run_page),
    url(r'^benchmark/', include(('benchmarks.urls', 'benchmarks'), namespace="benchmarks")),
    url(r'^task/', include(('tasks.urls', 'tasks'), namespace="tasks")),
    url(r'^scan/', include(('scans.urls', 'core'), namespace="scans")),
]
