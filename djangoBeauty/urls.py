from django.contrib import admin
from django.urls import path, include  # 必须导入 include

urlpatterns = [
    path('admin/', admin.site.urls),
    # 将 app 的路由挂载到 /api/ 下
    path('api/', include('app.urls')),
]