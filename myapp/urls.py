from django.urls import path
from . import views

urlpatterns = [
    #path('import_cars/<str:start_date>/<str:end_date>/',views.import_cars, name='import_cars'),
    path('import_cars/',views.import_cars, name='import_cars'),
    path('get_car/<int:car_id>/', views.get_car, name='get_car'),
    path('get_acc/<int:book_id>/', views.get_acc, name='get_acc'),
    path('update_car/<int:car_id>/', views.update_car, name='update_car'),
    path('send_booking_confirmation/', views.send_booking_confirmation, name='send_booking_confirmation'),
    path('update_taux/', views.update_taux, name='update_taux'),
    path('activation_car/<int:car_id>/', views.activation_car, name='activation_car'),
    path('get_all_cars/', views.get_all_cars, name='get_all_cars'),
    path('admin/get_cars_from_db/', views.get_cars_from_db, name='get_cars_from_db'),
    path('admin/get_cars_from_db_actives/', views.get_cars_from_db_actives, name='get_cars_from_db_actives'),
    path('add_car/', views.add_car, name='add_car'),
    path('add_acc/', views.add_acc, name='add_acc'),
    path('get_taux/', views.get_taux, name='get_taux'),
    path('add_book/', views.add_book, name='add_book'),
    path('update_book/<int:id_book>/', views.update_book, name='update_book'),
    path('update_acc/<int:id>/', views.update_acc, name='update_acc'),
    path('get_all_bookings/', views.get_all_bookings, name='get_all_bookings'),
    path('get_all_accessorys/', views.get_all_accessorys, name='get_all_accessorys'),
    path('get_all_styles/', views.get_all_styles, name='get_all_styles'),
    path('get_all_moteurs/', views.get_all_moteurs, name='get_all_moteurs'),
    path('get_all_radios/', views.get_all_radios, name='get_all_radios'),
    path('delete_all_cars/', views.delete_all_cars, name='delete_all_cars'),
    path('delete_car/<int:car_id>/', views.delete_car, name='delete_car'),
    path('api/logout/', views.logout_view, name='logout'),
    path('contact_view/', views.contact_view, name='contact_view'),
    path('get_all_contacts/', views.get_all_contacts, name='get_all_contacts'),

]
