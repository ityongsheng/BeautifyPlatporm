from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import UserProfile, Product, UserInteraction, RecommendationResult, ChatLog

# 注册扩展后的用户模型
@admin.register(UserProfile)
class UserProfileAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('美妆画像信息', {'fields': ('skin_type', 'age_group', 'allergens', 'is_profile_completed')}),
    )
    list_display = ('username', 'email', 'skin_type', 'is_staff')

# 注册商品模型，方便后台录入
@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'brand', 'category', 'price', 'suitable_skin')
    search_fields = ('title', 'brand')
    list_filter = ('category', 'suitable_skin')

# 注册其他模型，方便调试查看
admin.site.register(UserInteraction)
admin.site.register(RecommendationResult)
admin.site.register(ChatLog)