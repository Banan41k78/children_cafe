# kids_cafe/urls.py

from django.urls import path
from . import views

app_name = 'kids_cafe'   # namespace

urlpatterns = [
    path('', views.index, name='index'),
    path('catalog/', views.catalog, name='catalog'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('about/', views.about, name='about'),
    path('contacts/', views.contacts, name='contacts'),
    path('rental/', views.rental_form, name='rental_form'),
    path('job/', views.job_form, name='job_form'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('comment/add/<int:item_id>/', views.add_comment, name='add_comment'),
    path('comment/like/<int:comment_id>/', views.like_comment_ajax, name='like_comment_ajax'),
    path('feedback/', views.feedback_form, name='feedback_form'),
path('feedback/list/', views.feedback_list, name='feedback_list'),
]