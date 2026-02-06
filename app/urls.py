from django.urls import path
from .views import (
    RecommendAPIView, ChatAPIView, ProductDetailAPIView, 
    UserProfileStatsAPIView, ProductRankingAPIView, GlobalStatsAPIView,
    AdminStatsAPIView, AdminLogAPIView
)

urlpatterns = [
    # 用户端接口
    path('recommend/', RecommendAPIView.as_view(), name='recommend_api'),
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail_api'),
    path('user-stats/', UserProfileStatsAPIView.as_view(), name='user_stats_api'),
    path('rankings/', ProductRankingAPIView.as_view(), name='rankings_api'),
    path('global-stats/', GlobalStatsAPIView.as_view(), name='global_stats_api'),
    
    # 管理端接口
    path('admin/stats/', AdminStatsAPIView.as_view(), name='admin_stats_api'),
    path('admin/logs/', AdminLogAPIView.as_view(), name='admin_logs_api'),
    path('admin/logs/<int:pk>/correct/', AdminLogAPIView.as_view(), name='admin_log_correct_api'),
]