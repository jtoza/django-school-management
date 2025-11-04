from django.urls import path

from . import views

app_name = 'attendance'

urlpatterns = [
    path('', views.AttendanceRegisterListView.as_view(), name='register_list'),
    path('create/', views.AttendanceRegisterCreateView.as_view(), name='register_create'),
    path('<int:pk>/', views.AttendanceRegisterDetailView.as_view(), name='register_detail'),
    path('<int:pk>/edit/', views.AttendanceRegisterUpdateView.as_view(), name='register_edit'),
    path('<int:pk>/delete/', views.AttendanceRegisterDeleteView.as_view(), name='register_delete'),
    path('<int:pk>/take/', views.take_attendance, name='take_attendance'),
]