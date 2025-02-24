from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # ✅ Admin Panel Route
    path('admin/', admin.site.urls),

    # ✅ Authentication Routes
    path('login/', auth_views.LoginView.as_view(template_name='webapp/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),

    # ✅ Include all app routes from "webapp.urls"
    path('', include('webapp.urls')),
]
