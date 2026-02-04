from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings


# 1. 扩展用户模型：构建包含肤质特征的用户画像
class UserProfile(AbstractUser):
    """
    继承Django自带用户模型，增加美妆垂类特有的肤质画像字段。
    这些字段将作为'规则引擎'过滤推荐结果的核心依据。
    """
    SKIN_TYPE_CHOICES = (
        ('oil', '油性皮肤'),
        ('dry', '干性皮肤'),
        ('sensitive', '敏感肌肤'),
        ('combination', '混合性皮肤'),
        ('normal', '中性皮肤'),
    )

    # 核心画像数据
    skin_type = models.CharField(max_length=20, choices=SKIN_TYPE_CHOICES, default='normal', verbose_name="肤质类型")
    age_group = models.IntegerField(default=20, verbose_name="年龄段")
    allergens = models.CharField(max_length=255, blank=True, null=True, verbose_name="过敏源(逗号分隔)")

    # 记录用户是否完成了初始化设置（冷启动判断依据）
    is_profile_completed = models.BooleanField(default=False, verbose_name="画像是否完善")

    class Meta:
        verbose_name = "用户画像"
        verbose_name_plural = verbose_name


# 2. 商品信息模型：支撑AI语义分析与结构化展示
class Product(models.Model):
    """
    存储美妆商品的结构化数据。
    'ingredients'与'efficacy'字段将用于大模型生成推荐理由。
    """
    title = models.CharField(max_length=255, verbose_name="商品名称")
    brand = models.CharField(max_length=100, verbose_name="品牌")
    category = models.CharField(max_length=50, verbose_name="分类(水/乳/精华)")

    # 核心业务字段
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="价格")
    image_url = models.URLField(max_length=500, verbose_name="图片链接")

    # AI与规则引擎所需字段
    ingredients = models.TextField(verbose_name="核心成分", help_text="用于AI分析")
    efficacy = models.CharField(max_length=255, verbose_name="功效标签", help_text="如：保湿,抗衰,美白")
    suitable_skin = models.CharField(max_length=50, default='all', verbose_name="适用肤质", help_text="用于规则过滤")

    # 统计字段
    rating_avg = models.FloatField(default=0.0, verbose_name="平均评分")
    sales_count = models.IntegerField(default=0, verbose_name="销量")

    def __str__(self):
        return self.title


# 3. 用户交互行为模型：协同过滤算法的数据底座
class UserInteraction(models.Model):
    """
    记录用户的显性反馈（评分）与隐性反馈（浏览/点击）。
    此表数据将被Pandas读取，用于计算Item-CF相似度矩阵。
    """
    INTERACTION_TYPES = (
        ('view', '浏览'),
        ('click', '点击'),
        ('fav', '收藏'),
        ('rate', '评分'),
        ('buy', '购买'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='interactions')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='interactions')

    type = models.CharField(max_length=10, choices=INTERACTION_TYPES, verbose_name="交互类型")
    score = models.FloatField(default=0.0, verbose_name="评分权重(1-5)")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="发生时间")

    class Meta:
        verbose_name = "用户交互记录"
        unique_together = ('user', 'product', 'type')  # 防止重复记录


# 4. 推荐结果缓存表：存取分离，提升响应速度
class RecommendationResult(models.Model):
    """
    存储协同过滤算法计算后的Top-K推荐结果。
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    score = models.FloatField(verbose_name="推荐匹配度")
    reason = models.TextField(blank=True, null=True, verbose_name="AI推荐理由")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-score']

    # 5. AI对话日志：用于记录美妆顾问的交互历史


class ChatLog(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    user_input = models.TextField(verbose_name="用户提问")
    ai_response = models.TextField(verbose_name="AI回答")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "AI对话日志"