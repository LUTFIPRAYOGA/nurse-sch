"""mypso URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from scheduling import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('create', views.create),
    path('edit/<path:id>', views.edit),
    path('update/<path:id>', views.update),
    path('delete/<path:id>', views.destroy),
    path('beranda', views.beranda),
    path('pilihruang', views.pilihruang),
    path('pilihruang1', views.pilihruang1),
    path('pilihruang2', views.pilihruang2),
    path('dataperawat/<path:ruang>',views.dataperawat),
    path('perawat', views.perawat),
    path('demohah/demoedit',views.demo),
    path('suntingperawat/<path:ruang>',views.suntingperawat),
    path('kontak',views.kontak),
    path('result/<path:ruang>', views.result),
    path('start/<path:ruang>/<path:days>', views.start_pso),
    path('continue/<path:ruang>/<path:days>', views.continue_pso),
    path('grafik/<path:ruang>', views.view_graphic),
    path('statistik/<path:ruang>', views.view_statistic),
    path('print/<path:ruang>', views.generate_pdf)
]
