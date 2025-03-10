from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from . import views
from .views import (CapPivotView, CapYearlyView, cap_detail_view, export_to_excel,
    get_membership_data, status_pivot_view, status_pivot_dis_view, status_all_plans_view,
    status_by_plans_view, export_detail_to_excel, cap_detail_status_view)

urlpatterns = [
    # ✅ Authentication Routes
    path('', LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ✅ Dashboard Route
    path('home/', views.home, name='home'),

    # ✅ Membership Reports
    path('cap_pivot/', CapPivotView.as_view(), name='cap_pivot'),
    path('cap_pivot/<str:plan>/<str:capmo>/', cap_detail_view, name='cap_detail'),
    path('cap_yearly/', CapYearlyView.as_view(), name='cap_yearly'),

    # ✅ Export Routes (Excel)
    path('export_excel/<str:model_name>/', export_to_excel, name='export_excel'),
    # ✅ Nueva URL para exportar el detalle a Excel
    path('export_detail_excel/<str:plan>/<str:capmo>/', export_detail_to_excel, name='export_detail_to_excel'),

    # ✅ API Routes
    path('api/membership-data/', get_membership_data, name='membership_data'),
    path('api/status-data/', views.status_data, name='status_data'),

    # ✅ Status Reports (original)
    path('status_pivot/', status_pivot_view, name='status_pivot'),
    path('status_pivot_dis/', status_pivot_dis_view, name='status_pivot_dis'),

    # ✅ Nuevos reports de status
    path('status_all_plans/', status_all_plans_view, name='status_all_plans'),
    path('status_by_plans/', status_by_plans_view, name='status_by_plans'),

    path('api/status-data/', views.status_data, name='status_data'),

    path('status_detail/<str:stat>/<str:capmo>/', cap_detail_status_view, name='cap_detail_status'),

]