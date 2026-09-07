from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'

urlpatterns = [
    # ระบบสมาชิกและการจัดการสิทธิ์
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('admin/approval/', views.admin_approval_list, name='admin_approval'),
    path('admin/approval/action/<int:profile_id>/<str:action>/', views.update_status, name='update_status'),
    path('profile/', views.edit_profile, name='edit_profile'),

    # 1. หน้ากรอกอีเมลเพื่อขอรีเซ็ตรหัสผ่าน
    path(
        'password-reset/', 
        auth_views.PasswordResetView.as_view(
            template_name='password_reset.html',
            email_template_name='password_reset_email.html',
            success_url='/accounts/password-reset/done/'
        ), 
        name='password_reset'
    ),
    
    # 2. หน้าแจ้งเตือนว่าระบบได้ส่งอีเมลไปแล้ว
    path(
        'password-reset/done/', 
        auth_views.PasswordResetDoneView.as_view(
            template_name='password_reset_done.html'
        ), 
        name='password_reset_done'
    ),
    
    # 3. ลิงก์ที่ส่งไปในอีเมล เพื่อให้ผู้ใช้คลิกเข้ามาตั้งรหัสผ่านใหม่
    path(
        'password-reset-confirm/<uidb64>/<token>/', 
        auth_views.PasswordResetConfirmView.as_view(
            template_name='password_reset_confirm.html',
            success_url='/accounts/password-reset-complete/'
        ), 
        name='password_reset_confirm'
    ),
    
    # 4. หน้าแจ้งเตือนว่าเปลี่ยนรหัสผ่านสำเร็จแล้ว
    path(
        'password-reset-complete/', 
        auth_views.PasswordResetCompleteView.as_view(
            template_name='password_reset_complete.html'
        ), 
        name='password_reset_complete'
    ),
]