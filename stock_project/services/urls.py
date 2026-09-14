from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # หน้าแสดงรายการงานซ่อม (หน้าหลักของ services)
    path('', views.job_list, name='job_list'),
    path('history/', views.job_history, name='job_history'), # เพิ่มบรรทัดนี้
    path('create/', views.create_service_job, name='create_job'),
    path('edit/<int:job_id>/', views.edit_service_job, name='edit_job'),
    path('submit/<int:job_id>/', views.submit_service_job, name='submit_job'),
]