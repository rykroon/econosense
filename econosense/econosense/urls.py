"""econosense URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
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
from django.urls import path
from data.views import BestPlacesToWorkView,RentToIncomeRatioView
from data.ajax import JobAutocomplete,LocationAutocomplete,BestPlacesToWorkAjax,RentToIncomeRatioAjax
from main.views import home

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home),
    path('best-places-to-work/',BestPlacesToWorkView.as_view()),
    path('rent-to-income-ratio/',RentToIncomeRatioView.as_view()),
    #path('data-table-test/',data_table_test),
    path('ajax/jobs/',JobAutocomplete.as_view()),
    path('ajax/locations/',LocationAutocomplete.as_view()),
    path('ajax/best-places-to-work',BestPlacesToWorkAjax.as_view()),
    path('ajax/rent-to-income-ratio',RentToIncomeRatioAjax.as_view())
]
