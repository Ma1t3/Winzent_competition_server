"""PGASC URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.0/topics/http/urls/
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
from django.contrib import admin
from django.urls import path, include

from pgasc.web.home import views as home_views
from pgasc.web.usermanagement import views as usermanagement_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", home_views.home, name="home"),
    path("howto/", home_views.howto, name="howto"),
    path(
        "testuser_login",
        home_views.create_test_user_and_log_in,
        name="testuser_login",
    ),
    path("user/register", usermanagement_views.register, name="register"),
    path("user/", include("django.contrib.auth.urls")),
    path(
        "user/ajax/set_list_autoreload",
        usermanagement_views.set_list_autoreload,
        name="set_list_autoreload",
    ),
    path("agent/", include("pgasc.web.agentsystemmanagement.urls")),
    path(
        "experiment/", include("pgasc.web.experimentdefinitionmanagement.urls")
    ),
    path(
        "experiment/", include("pgasc.web.experimentexecutionmanagement.urls")
    ),
    path(
        "competition/",
        include("pgasc.web.competitiondefinitionmanagement.urls"),
    ),
]
