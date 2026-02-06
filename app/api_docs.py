import json
import os

def generate_api_docs():
    """
    Automated API Documentation Generator (Swagger-style JSON)
    """
    docs = {
        "swagger": "2.0",
        "info": {
            "title": "Beauty Platform AI API",
            "description": "美妆垂类大模型推荐系统接口文档",
            "version": "2.0.0"
        },
        "paths": {
            "/api/recommend/": {
                "get": {
                    "summary": "获取个性化推荐 (Get Personalized Recommendations)",
                    "parameters": [{"name": "user_id", "in": "query", "required": True}]
                }
            },
            "/api/chat/": {
                "post": {
                    "summary": "AI 美妆顾问对话 (AI Makeup Consultant Chat)",
                    "parameters": [{"name": "message", "in": "body", "required": True}]
                }
            },
            "/api/admin/stats/": {
                "get": { "summary": "全平台运营数据大屏 (System Analytics Dashboard)" }
            }
        }
    }
    return docs

def generate_algo_flowchart():
    """
    Generates Mermaid logic for the recommendation algorithm
    """
    mermaid = """
    graph TD
      A[用户画像/行为数据] --> B{三路召回引擎}
      B --> C[协同过滤召回: 挖掘历史相似性]
      B --> D[内容属性召回: 解决冷启动]
      B --> E[安全性召回: 过滤过敏源/禁忌]
      C --> F[加权融合排序 Weighted Hybrid]
      D --> F
      E --> F
      F --> G[RAG-Lite: 结合知识库生成理由]
      G --> H[最终推荐列表]
    """
    return mermaid

if __name__ == "__main__":
    # Exporting
    with open('api_spec.json', 'w', encoding='utf-8') as f:
        json.dump(generate_api_docs(), f, ensure_ascii=False, indent=2)
    
    with open('algo_logic.md', 'w', encoding='utf-8') as f:
        f.write("# Recommendation Logic Flow\n\n```mermaid\n" + generate_algo_flowchart() + "\n```")
    
    print("Documentation exported to api_spec.json and algo_logic.md")
