from django.urls import path
from .views import PdfTestView

app_name = 'pdf'

urlpatterns = [
    path('test/print/', PdfTestView.as_view(), {'for_download': False, 'lines': 200, }, name="test-print"),
    path('test/download/', PdfTestView.as_view(), {'for_download': True, 'lines': 200, }, name="test-download"),
]

