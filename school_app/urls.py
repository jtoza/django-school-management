from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.generic import RedirectView
from django.shortcuts import redirect

# Custom redirect view to handle the accounts/login issue
def redirect_to_login(request):
    return redirect('/login/')

urlpatterns = [
    # Handle the accounts/login/ URL that Django's auth system expects
    path('accounts/login/', redirect_to_login),
    path('accounts/logout/', RedirectView.as_view(pattern_name='logout', permanent=True)),
    
    path('admin/', admin.site.urls),
    path('', include('apps.corecode.urls')),
    path('students/', include('apps.students.urls')),
    path('staffs/', include('apps.staffs.urls')),
    path('finance/', include('apps.finance.urls')),
    path('result/', include('apps.result.urls')),
    path('attendance/', include('attendance.urls', namespace='attendance')),
    
    # PWA URLs - serve static files directly
    path('manifest.json', serve, {
        'path': 'manifest.json',
        'content_type': 'application/json'
    }),
    path('service-worker.js', serve, {
        'path': 'js/sw.js',
        'content_type': 'application/javascript'
    }),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)