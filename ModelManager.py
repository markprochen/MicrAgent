import yaml
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

class ModelManager:
    def __init__(self, config_path="./config/models.yaml"):
        with open(config_path, 'r', encoding='utf-8') as f:
            self.config = yaml.safe_load(f)
        self.models = {}
        self._init_models()

    def get_models_menu(self):
        """生成供用户选择的菜单文本"""
        menu = "\n--- 可用大脑列表 ---"
        for cfg in self.config['models']:
            is_default = "[默认]" if cfg.get('default') else ""
            menu += f"\n- {cfg['id']}: {cfg['description']} ({cfg['name']}) {is_default}"
        menu += "\n--------------------\n"
        menu += "输入 /use [id] 切换模型 (例如: /use coder)\n"
        return menu
    def get_all_ids(self):
        """返回所有合法的模型 ID 列表"""
        return [cfg['id'] for cfg in self.config['models']]
    
    def _init_models(self):
        for cfg in self.config['models']:
            if cfg['provider'] == 'local':
                instance = ChatOllama(model=cfg['name'], temperature=0.6)
            else:
                instance = ChatOpenAI(
                    model=cfg['name'],
                    api_key=cfg.get('api_key'),
                    base_url=cfg.get('base_url'),
                    temperature=0.6
                )
            self.models[cfg['id']] = instance

    def get_model(self, model_id=None):
        # 如果没指定，返回默认模型
        if not model_id:
            for cfg in self.config['models']:
                if cfg.get('default'): return self.models[cfg['id']]
        return self.models.get(model_id)