from django.urls import path
from . import views

urlpatterns = [
    path('', views.part_list, name='part_list'),
    path('add/', views.part_create, name='part_create'),
    path('edit/<int:pk>/', views.part_update, name='part_update'),
    path('delete/<int:pk>/', views.part_delete, name='part_delete'),
    path('transaction/add/', views.transaction_create, name='transaction_create'),
    path('transaction/history/', views.transaction_history, name='transaction_history'),
    path('transactions/export/', views.export_transactions_excel, name='export_transactions_excel'),
]