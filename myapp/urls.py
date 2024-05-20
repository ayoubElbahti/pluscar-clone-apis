from django.urls import path
from . import views

urlpatterns = [
    path('hello/', views.hello_world, name='hello_world'),
    path('download_fb_video/', views.download_fb_video, name='download_fb_video'),
    path('get_cars/', views.get_cars, name='get_cars'),
    path('details/', views.details, name='details'),
    path('get_all_cars/<str:start_date>/<str:end_date>/',views.get_details, name='get_details'),
]