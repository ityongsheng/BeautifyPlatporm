import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from .models import UserInteraction, Product, UserProfile
from .knowledge_service import KnowledgeService
from openai import OpenAI
import random

# === Configuration / 配置区域 ===
# API connection details for the LLM component.
# 大语言模型组件的 API 连接详情。
API_KEY = "sk-edb3fee01eac43cb9ab0b695ad6bdfcc"
BASE_URL = "https://api.deepseek.com"

ks = KnowledgeService()

def generate_ai_reason(product, skin_type):
    """
    RAG-Lite: Combine local knowledge base with LLM to generate professional recommendation reasons.
    双语注释：RAG-Lite模式 - 结合本地知识库与大语言模型生成专业推荐理由。
    
    Args:
        product: Product model instance.
        skin_type: User's skin type string.
    """
    ingredients = [i.strip() for i in product.ingredients.split(',')]
    
    # 1. Retrieve domain knowledge from Local KB / 从本地知识库获取领域专业知识
    professional_context = ks.get_professional_reason(ingredients)
    
    # Check if a valid API key is provided / 检查是否提供了有效的 API 密钥
    if "sk-XXX" in API_KEY or not API_KEY:
        return f"【专业点评】{professional_context}"

    try:
        client = OpenAI(api_key=API_KEY, base_url=BASE_URL)
        prompt = f"""
        你是一名专业的皮肤科医生。用户肤质：{skin_type}。推荐商品：{product.title}。
        专业成分分析：{professional_context}。请生成50字以内的专业推荐理由。
        """
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=[
                {"role": "system", "content": "你是一个严谨且专业的护肤成分分析助手。"},
                {"role": "user", "content": prompt}
            ],
            stream=False
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Fallback to local KB explanation if API fails / API 调用失败时回退回本地知识库解释
        return f"【成分解析】{professional_context}"

def get_behavioral_recall(user_id, top_n=20):
    """
    Recall Phase 1: Item-based Collaborative Filtering.
    召回阶段1：基于物品的协同过滤。
    Uses Cosine Similarity on user-item interaction matrix to find patterns in user preferences.
    使用余弦相似度在用户-商品交互矩阵上挖掘用户偏好模式。
    """
    interactions = UserInteraction.objects.all().values('user_id', 'product_id', 'score')
    if not interactions: return {}

    # Convert interaction data to a DataFrame / 将交互数据转换为 DataFrame
    df = pd.DataFrame(list(interactions))
    user_item_matrix = df.pivot_table(index='user_id', columns='product_id', values='score').fillna(0)

    if user_id not in user_item_matrix.index: return {}

    # Calculate item-item similarity matrix / 计算商品-对-商品的相似度矩阵
    item_sim = cosine_similarity(user_item_matrix.T)
    item_sim_df = pd.DataFrame(item_sim, index=user_item_matrix.columns, columns=user_item_matrix.columns)

    user_vec = user_item_matrix.loc[user_id]
    interacted_items = user_vec[user_vec > 0].index.tolist()
    
    scores = {}
    for item_id in interacted_items:
        # Get most similar items / 获取最相似的商品
        sim_items = item_sim_df[item_id].sort_values(ascending=False)[1:top_n+1]
        for sim_id, score in sim_items.items():
            if sim_id in interacted_items: continue
            scores[sim_id] = scores.get(sim_id, 0) + score
    return scores

def get_content_recall(user_profile, top_n=20):
    """
    Recall Phase 2: Content-based Filtering.
    召回阶段2：基于内容属性的过滤。
    Designed to solve the "Cold Start" problem for items or users with no interaction history.
    旨在解决没有任何交互历史的商品或用户的“冷启动”问题。
    """
    # Filter products based on skin type compatibility / 根据肤质兼容性过滤商品
    candidates = Product.objects.filter(suitable_skin__in=[user_profile.skin_type, 'all'])
    scores = {prod.id: (0.8 if prod.suitable_skin == user_profile.skin_type else 0.5) for prod in candidates[:top_n*2]}
    return scores

def safety_filter(candidates, user_profile):
    """
    Recall Phase 3: Safety Guardrails (Rule-based filtering).
    召回阶段3：安全性护栏（基于规则的过滤）。
    A mandatory security layer to prevent harmful recommendations.
    防止产生有害推荐的强制性安全层。
    """
    filtered = []
    allergens = [a.strip() for a in (user_profile.allergens or "").split(',') if a.strip()]
    
    for product_id, score in candidates.items():
        try:
            product = Product.objects.get(id=product_id)
            # Sensitive skin check for alcohol / 敏感肌检查是否含酒精
            if user_profile.skin_type == 'sensitive' and '酒精' in product.ingredients: continue
            # Check for specific user allergens / 检查用户特定的过敏源
            if any(a in product.ingredients for a in allergens): continue
            filtered.append((product, score))
        except Product.DoesNotExist: continue
    return filtered

def recommend_products(user_id, top_k=5):
    """
    Core Entry: Hybrid Recommendation Engine (Tiple-Path Recall + Safety Filtering).
    核心入口：混合推荐引擎（三路召回 + 安全过滤）。
    
    Strategy: Combines statistical behaviors with semantic content.
    策略：将统计行为与语义内容相结合。
    """
    try:
        user = UserProfile.objects.get(id=user_id)
    except UserProfile.DoesNotExist: return []

    # 1. Multi-path Recall Execution / 执行多路召回
    behavior_scores = get_behavioral_recall(user_id)
    content_scores = get_content_recall(user)
    
    # 2. Hybrid Score Fusion (Weighted Merge) / 混合评分融合（加权合并）
    merged_candidates = {}
    for pid, score in behavior_scores.items(): merged_candidates[pid] = score * 0.7
    for pid, score in content_scores.items(): merged_candidates[pid] = merged_candidates.get(pid, 0) + score * 0.3
        
    # 3. Apply Safety and Logic Filter / 应用安全与逻辑过滤
    safe_candidates = safety_filter(merged_candidates, user)
    
    # 4. Final Ranking / 最终排序
    sorted_candidates = sorted(safe_candidates, key=lambda x: x[1], reverse=True)[:top_k]
    
    # 5. Populate Results with AI-assisted Reasons / 使用 AI 辅助生成的理由填充结果
    results = []
    for i, (product, score) in enumerate(sorted_candidates):
        # AI generate reason only for the top item to optimize latency / 仅对顶部商品生成 AI 理由以优化延迟
        is_val_key = API_KEY and not API_KEY.startswith("sk-XXX")
        reason = generate_ai_reason(product, user.skin_type) if (i == 0 and is_val_key) else \
                 ks.get_professional_reason([i.strip() for i in product.ingredients.split(',')])
             
        results.append({
            'product_id': product.id, 
            'title': product.title,
            'score': round(float(score), 2) if score > 0 else 0.85,
            'reason': reason, 
            'brand': product.brand, 
            'price': float(product.price)
        })
    return results