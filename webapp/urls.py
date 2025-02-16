from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from . import views
from .views import cap_detail_view, CapPivotView  # Elimina cap_pivot_view

urlpatterns = [
    path('', LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('home/', views.home, name='home'),
    path('report/', views.show_query_result, name='show_query_result'),
    path('export_csv/', views.export_csv, name='export_csv'),
    path('export_pdf/', views.export_pdf, name='export_pdf'),
    path('cap_pivot/', CapPivotView.as_view(), name='cap_pivot'),  # CBV requiere .as_view()
    path('cap_pivot/<str:plan>/<str:capmo>/', cap_detail_view, name='cap_detail'),
]
