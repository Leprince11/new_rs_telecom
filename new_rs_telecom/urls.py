# from django.conf import settings
# from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from new_rs_telecom import settings

urlpatterns = [
    path('',include('portail_web.urls')),
    path('admin/',include('pulls.urls')),
    path('rstelecom/', include('tests.urls')),

]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

