from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include("users.urls")),
    path('', include("products.urls")),
    path('subs/', include("subscriptions.urls")),
    path('payments/', include("payments.urls"))
]
