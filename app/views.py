from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import UserProfile
from .recommend_algo import collaborative_filtering_recommendation
from .serializers import ProductSerializer


class RecommendAPIView(APIView):
    """
    GET /api/recommend/?user_id=1
    获取指定用户的个性化推荐结果
    """

    def get(self, request):
        # 1. 获取 user_id 参数
        user_id = request.query_params.get('user_id')

        if not user_id:
            return Response({"error": "请提供 user_id 参数"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # 2. 检查用户是否存在
            user = UserProfile.objects.get(id=user_id)
        except UserProfile.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)

        # 3. 调用你的核心算法 (Item-CF + 规则过滤)
        # 注意：这里我们调用之前写好的函数
        recommend_list = collaborative_filtering_recommendation(user.id, top_k=5)

        # 4. 返回结果
        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "skin_type": user.skin_type
            },
            "recommendations": recommend_list
        }, status=status.HTTP_200_OK)


from openai import OpenAI

# 请确保这里填入了你的 Key，或者从 recommend_algo 导入配置
API_KEY = "sk-edb3fee01eac43cb9ab0b695ad6bdfcc"
BASE_URL = "https://api.deepseek.com"


class ChatAPIView(APIView):
    """
    POST /api/chat/
    简单的 AI 对话接口
    """

    def post(self, request):
        user_message = request.data.get('message')
        if not user_message:
            return Response({"error": "内容不能为空"}, status=status.HTTP_400_BAD_REQUEST)

        # 模拟模式 (如果没有 Key)
        if "sk-xxx" in API_KEY:
            return Response({
                "reply": f"【模拟回复】您刚才说了：{user_message}。由于未配置真实Key，我是个复读机。"
            })

        try:
            client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
            response = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "你是一位专业的皮肤科医生和美妆顾问，语气温柔，回答简练。"},
                    {"role": "user", "content": user_message},
                ],
                stream=False
            )
            ai_reply = response.choices[0].message.content.strip()
            return Response({"reply": ai_reply})

        except Exception as e:
            print(f"Chat Error: {e}")
            return Response({"reply": "AI 大脑由于网络原因暂时短路了，请稍后再试。"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ProductDetailAPIView(APIView):
    """
    GET /api/product/<id>/
    获取商品详情
    """
    def get(self, request, pk):
        try:
            from .models import Product
            product = Product.objects.get(pk=pk)
            serializer = ProductSerializer(product)
            return Response(serializer.data)
        except Product.DoesNotExist:
            return Response({"error": "商品不存在"}, status=status.HTTP_404_NOT_FOUND)


class UserProfileStatsAPIView(APIView):
    """
    GET /api/user-stats/?user_id=1
    获取用户肤质分析数据（用于雷达图）
    """
    def get(self, request):
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response({"error": "缺少 user_id"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user = UserProfile.objects.get(id=user_id)
            # 模拟肤质分析数据（实际项目中可根据用户交互和算法得出）
            # 维：水分, 油分, 敏感度, 弹性, 光泽
            stats = {
                "oil": 85 if user.skin_type == 'oil' else (30 if user.skin_type == 'dry' else 50),
                "moisture": 30 if user.skin_type == 'dry' else 60,
                "sensitivity": 90 if user.skin_type == 'sensitive' else 20,
                "elasticity": 75,
                "shining": 65
            }
            return Response({
                "username": user.username,
                "skin_type": user.get_skin_type_display(),
                "stats": stats
            })
        except UserProfile.DoesNotExist:
            return Response({"error": "用户不存在"}, status=status.HTTP_404_NOT_FOUND)


class ProductRankingAPIView(APIView):
    """
    GET /api/rankings/
    获取热门榜单
    """
    def get(self, request):
        from .models import Product
        # 简单逻辑：按评分和销量综合排序
        products = Product.objects.order_by('-rating_avg', '-sales_count')[:10]
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)