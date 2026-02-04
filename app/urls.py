from django.urls import path
from .views import RecommendAPIView, ChatAPIView, ProductDetailAPIView, UserProfileStatsAPIView, ProductRankingAPIView

urlpatterns = [
    path('recommend/', RecommendAPIView.as_view(), name='recommend_api'),
    path('chat/', ChatAPIView.as_view(), name='chat_api'),
    path('product/<int:pk>/', ProductDetailAPIView.as_view(), name='product_detail_api'),
    path('user-stats/', UserProfileStatsAPIView.as_view(), name='user_stats_api'),
    path('rankings/', ProductRankingAPIView.as_view(), name='rankings_api'),
]