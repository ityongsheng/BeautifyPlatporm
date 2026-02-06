import json
import os

class KnowledgeService:
    _instance = None
    _kb_data = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(KnowledgeService, cls).__new__(cls)
            cls._instance._load_kb()
        return cls._instance

    def _load_kb(self):
        kb_path = os.path.join(os.path.dirname(__file__), 'knowledge_base.json')
        try:
            with open(kb_path, 'r', encoding='utf-8') as f:
                self._kb_data = json.load(f)
        except Exception as e:
            print(f"Error loading knowledge base: {e}")
            self._kb_data = []

    def get_ingredient_info(self, ingredient_name):
        if not self._kb_data:
            return None
        for item in self._kb_data:
            if item['name'] == ingredient_name or ingredient_name in item['aliases']:
                return item
        return None

    def get_professional_reason(self, ingredient_list):
        reasons = []
        for ing in ingredient_list:
            info = self.get_ingredient_info(ing)
            if info:
                reasons.append(f"{info['name']}（{info['benefits']}）")
        
        if not reasons:
            return "该产品含有多种有效成分，能满足您的护肤需求。"
        
        return "含有" + "、".join(reasons) + "，非常适合您的肤质。"
