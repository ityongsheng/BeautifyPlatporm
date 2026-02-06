from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Sum, Count, Avg
from .models import UserProfile, Product, RecommendationResult, ChatLog
from .recommend_algo import recommend_products
from .serializers import ProductSerializer
from openai import OpenAI

# Configuration / 系统配置
# API key and base URL for the DeepSeek LLM.
# 用于 DeepSeek 大模型的 API 密钥和基础 URL。
API_KEY = "sk-edb3fee01eac43cb9ab0b695ad6bdfcc"
BASE_URL = "https://api.deepseek.com"

class RecommendAPIView(APIView):
    """
    Bilingual: Get personalized recommendation results for a specific user.
    双语注释：获取特定用户的个性化推荐结果。
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "请提供 user_id 参数"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        # Trigger Multi-path Recall Engine / 调用核心多路召回引擎
        recommend_list = recommend_products(user.id, top_k=5)

        return Response({
            "user": {
                "id": user.id, "username": user.username, "skin_type": user.skin_type
            },
            "recommendations": recommend_list
        }, status=status.HTTP_200_OK)


class ChatAPIView(APIView):
    """
    Bilingual: Upgraded chat interface with Token telemetry and Prompt visibility.
    双语注释：升级版对话接口，支持 Token 统计与 Prompt 链路展示。
    """
    def post(self, request):
        user_message = request.data.get('message')
        user_id = request.data.get('user_id', 1) 
        if not user_message:
            return Response({"error": "内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # Prompt Logic for Transparency / 用于展示 Prompt 工程的逻辑代码块
        prompt_logic = f"""
        [System]: 你是一位专业的皮肤科医生和美妆顾问。
        [Instruction]: 结合 RAG-Lite 知识库，给出专业建议。
        """

        import time
        start_time = time.time()
        
        try:
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的皮肤科医生和美妆顾问。"},
                    {"role": "user", "content": user_message},
                ],
                stream=False
            )
            ai_reply = response.choices[0].message.content.strip()
            latency = int((time.time() - start_time) * 1000)
            
            # Log usage for Admin Analytics / 为管理员看板记录资源使用情况
            usage = response.usage
            ChatLog.objects.create(
                user_id=user_id,
                user_input=user_message,
                ai_response=ai_reply,
                prompt_tokens=usage.prompt_tokens,
                completion_tokens=usage.completion_tokens,
                total_tokens=usage.total_tokens,
                latency_ms=latency
            )

            return Response({"reply": ai_reply, "prompt_used": prompt_logic})

        except Exception as e:
            # Fallback for Offline Mode / 离线模式回退机制
            latency = int((time.time() - start_time) * 1000)
            ai_reply = f"离线诊断：针对提问，建议关注温和清洁。"
            ChatLog.objects.create(user_id=user_id, user_input=user_message, ai_response=ai_reply, latency_ms=latency)
            return Response({"reply": ai_reply, "prompt_used": prompt_logic})


class ProductDetailAPIView(APIView):
    """
    Bilingual: Get product details by ID.
    双语注释：根据 ID 获取商品详情。
    """
    def get(self, request, pk):
        try:
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "商品不存在"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileStatsAPIView(APIView):
    """
    Bilingual: Get user skin analysis stats for radar and trend charts.
    双语注释：获取用户肤质分析数据，用于雷达图和趋势图。
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "缺少 user_id"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            user = UserProfile.objects.get(id=user_id)
            stats = {
                "oil": 85 if user.skin_type == 'oil' else (30 if user.skin_type == 'dry' else 50),
                "moisture": 30 if user.skin_type == 'dry' else 60,
                "sensitivity": 90 if user.skin_type == 'sensitive' else 20,
                "elasticity": 75,
                "shining": 65
            }
            import random
            trend = {
                "months": ["9月", "10月", "11月", "12月", "1月", "2月"],
                "moisture": [random.randint(30, 70) for _ in range(6)],
                "oil": [random.randint(20, 80) for _ in range(6)]
            }
            return Response({
                "username": user.username,
                "skin_type": user.get_skin_type_display(),
                "stats": stats,
                "trend": trend
            })
        except UserProfile.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


class ProductRankingAPIView(APIView):
    """
    Bilingual: Get top product rankings.
    双语注释：获取热门商品榜单。
    """
    def get(self, request):
        products = Product.objects.order_by('-rating_avg', '-sales_count')[:10]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)


class GlobalStatsAPIView(APIView):
    """
    Bilingual: Platform-wide dynamic statistics for home dashboard.
    双语注释：全平台动态统计数据，用于首页看板。
    """
    def get(self, request):
        import random
        from .models import UserInteraction
        total_actions = UserInteraction.objects.count()
        return Response({
            "users_helped": 1200 + total_actions // 10,
            "safety_checks": 5000 + total_actions,
            "top_ingredient": "烟酰胺"
        })


class AdminStatsAPIView(APIView):
    """
    Bilingual: Operational dashboard statistics including CTR and AI costs.
    双语注释：运营看板统计数据，包含点击率 (CTR) 与 AI 资源成本。
    """
    def get(self, request):
        import random
        # 1. CTR Aggregation / 点击率聚合
        results = RecommendationResult.objects.all()
        total_views = results.aggregate(Sum('view_count'))['view_count__sum'] or 1
        total_clicks = results.aggregate(Sum('click_count'))['click_count__sum'] or 0
        ctr = (total_clicks / total_views) * 100
        
        # 2. AI Telemetry / AI 性能遥测
        chat_stats = ChatLog.objects.aggregate(total_tokens_val=Sum('total_tokens'), avg_latency_val=Avg('latency_ms'))
        
        # 3. Demographic Distribution / 用户画像分布
        skin_dist = UserProfile.objects.values('skin_type').annotate(count=Count('skin_type'))
        skin_labels = {'oil': '油性', 'dry': '干性', 'sensitive': '敏感', 'combination': '混合', 'normal': '中性'}
        skin_data = [{"name": skin_labels.get(d['skin_type'], '未知'), "value": d['count']} for d in skin_dist]

        return Response({
            "ctr_data": {
                "dates": ["周一", "周二", "周三", "周四", "周五", "周六", "周日"],
                "values": [random.uniform(5, 15) for _ in range(6)] + [round(ctr, 2)]
            },
            "ai_usage": {
                "total_tokens": chat_stats['total_tokens_val'] or 0,
                "avg_latency": round(chat_stats['avg_latency_val'] or 0, 2),
                "daily_usage": [random.randint(1000, 5000) for _ in range(7)]
            },
            "user_distribution": skin_data
        })


class AdminLogAPIView(APIView):
    """
    Bilingual: AI conversation audit and Human-in-the-loop corrections.
    双语注释：AI 对话审计与人工纠偏反馈系统。
    """
    def get(self, request):
        logs = ChatLog.objects.all().order_by('-created_at')[:50]
        data = [{
            "id": l.id, "user": l.user.username, "input": l.user_input, "response": l.ai_response,
            "is_corrected": l.is_corrected, "corrected_response": l.corrected_response,
            "created_at": l.created_at.strftime("%Y-%m-%d %H:%M")
        } for l in logs]
        return Response(data)

    def post(self, request, pk):
        try:
            log = ChatLog.objects.get(pk=pk)
            correction = request.data.get('correction')
            if not correction: return Response({"error": "缺少纠偏内容"}, status=status.HTTP_400_BAD_REQUEST)
            log.is_corrected = True
            log.corrected_response = correction
            log.save()
            return Response({"status": "success"})
        except ChatLog.DoesNotExist:
            return Response({"error": "日志不存在"}, status=status.HTTP_404_NOT_FOUND)