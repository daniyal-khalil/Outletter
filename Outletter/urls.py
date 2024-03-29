"""Outletter URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.conf.urls.static import static
from django.conf import settings 

urlpatterns = [
    path('admin/', admin.site.urls),
    path("api/v1/", include("Outletter.api.user.urls"), name="user_api"),
    path("api/v1/", include("Outletter.api.item.urls"), name="item_api"),
    path("api/v1/", include("Outletter.api.review.urls"), name="review_api"),
    path("api/v1/", include("Outletter.api.like.urls"), name="like_api"),
    path("api/v1/", include("Outletter.api.wish.urls"), name="wish_api"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path('api-auth/', include('rest_framework.urls'))
]