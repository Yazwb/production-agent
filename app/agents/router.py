from app.domain.enums import Domain


class IntentRouter:
    """MVP 采用关键词路由，后续可替换为分类模型或 LLM Router。"""
    KEYWORDS = {
        Domain.EQUIPMENT: ("设备", "故障", "轴承", "振动", "维护", "停机", "烘干机"),
        Domain.QUALITY: ("质量", "缺陷", "良率", "质检", "不合格", "含水率"),
        Domain.PROCESS: ("工艺", "参数", "流程", "温度", "风速", "生产"),
    }

    def route(self, question: str, requested: Domain) -> Domain:
        # 用户显式选择领域时优先使用用户选择，避免自动分类覆盖人工判断。
        if requested is not Domain.AUTO:
            return requested
        scores = {domain: sum(keyword in question for keyword in keywords) for domain, keywords in self.KEYWORDS.items()}
        return max(scores, key=scores.get) if max(scores.values()) else Domain.PROCESS
