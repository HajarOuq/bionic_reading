from django.urls import path
from .views import process_text, history_view, view_entry, delete_entry, download_pdf

urlpatterns = [
    path('', process_text, name='process_text'),
    path('history/', history_view, name='history'),
    path('view/<int:pk>/', view_entry, name='view_entry'),
    path('download/pdf/<int:pk>/', download_pdf, name='download_pdf'),
    path('delete/<int:pk>/', delete_entry, name='delete_entry'),
]
