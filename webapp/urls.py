from django.urls import path
from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LoginView
from . import views
from .views import CapPivotView, CapYearlyView, cap_detail_view, export_to_csv, export_to_pdf, get_membership_data
from .views import status_pivot_view, status_pivot_dis_view
from .views import export_detail_to_csv, export_detail_to_pdf

urlpatterns = [
    # ✅ Login and Logout
    path('', LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ✅ Main Dashboard Page
    path('home/', views.home, name='home'),

    # ✅ Pivot Table Report (12 Months Membership)
    path('cap_pivot/', CapPivotView.as_view(), name='cap_pivot'),
    path('cap_pivot/<str:plan>/<str:capmo>/', cap_detail_view, name='cap_detail'),

    # ✅ Generic Export to CSV and PDF
    path('export_csv/<str:model_name>/', export_to_csv, name='export_csv'),
    path('export_pdf/<str:model_name>/', export_to_pdf, name='export_pdf'),

    # ✅ API Endpoint for Membership Data (Used in Doughnut Chart)
    path('api/membership-data/', get_membership_data, name='membership_data'),

    # ✅ Pivot Table Report (By Year Membership)
        path('cap_yearly/', CapYearlyView.as_view(), name='cap_yearly'),

    # ✅ Agregar las nuevas rutas en urlpatterns
    path('status_pivot/', status_pivot_view, name='status_pivot'),
    path('status_pivot_dis/', status_pivot_dis_view, name='status_pivot_dis'),

    # ✅ Exportación de reportes detallados (Membership Detail)
    path('export_detail_csv/<str:plan>/<str:capmo>/', export_detail_to_csv, name='export_detail_to_csv'),
    path('export_detail_pdf/<str:plan>/<str:capmo>/', export_detail_to_pdf, name='export_detail_to_pdf'),

]
