from django.urls import path
from . import views

urlpatterns = [
    path('',views.dashboard,name='dashboard'),
    path('products/',views.product_list,name='product_list'),
    path('products/upload/',views.product_upload,name='product_upload'),
    path('product/download/',views.product_download,name='product_download'),
]