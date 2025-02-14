from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('login/', auth_views.LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('report/', views.show_query_result, name='show_query_result'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_pdf/', views.export_pdf, name='export_pdf'),
]
