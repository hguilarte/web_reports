from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from . import views
from .views import cap_pivot_view, cap_detail_view

urlpatterns = [
    path('', LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('login/', auth_views.LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('', views.home, name='home'),
    path('report/', views.show_query_result, name='show_query_result'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_pdf/', views.export_pdf, name='export_pdf'),
    path('cap_pivot/', cap_pivot_view, name='cap_pivot'),
    path('cap_pivot/<str:plan>/<str:capmo>/', cap_detail_view, name='cap_detail'),
]
