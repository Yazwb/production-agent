import json
from urllib.request import Request, urlopen

from app.domain.models import Chunk


class ExtractiveLanguageModel:
    """无外部模型时的降级实现，用检索片段直接构造可验证的回答。"""
    def answer(self, _: str, context: list[Chunk]) -> str:
        if not context:
            return "知识库中没有检索到相关信息，请补充资料或换一种问法。"
        excerpts = "\n".join(f"{index}. {chunk.text}" for index, chunk in enumerate(context[:3], 1))
        return f"当前为本地检索模式，以下是知识库中的相关依据：\n{excerpts}"


class OpenAICompatibleLanguageModel:
    """调用 vLLM、Ollama 或其他兼容 Chat Completions 协议的服务。"""
    def __init__(self, base_url: str, api_key: str, model: str) -> None:
        self.url = base_url.rstrip("/") + "/chat/completions"
        self.api_key = api_key
        self.model = model

    def answer(self, question: str, context: list[Chunk]) -> str:
        if not context:
            return "知识库中没有检索到相关信息，请补充资料或换一种问法。"
        # 将文件名和页码一并放进上下文，便于模型回答时引用来源。
        evidence = "\n\n".join(
            f"[资料{index}] {chunk.filename} 第{chunk.page_number}页\n{chunk.text}"
            for index, chunk in enumerate(context, 1)
        )
        payload = {
            "model": self.model,
            "temperature": 0.1,
            "messages": [
                {"role": "system", "content": "你是工业知识助手。只能根据资料回答；资料不足时明确说明，不得编造。"},
                {"role": "user", "content": f"资料：\n{evidence}\n\n问题：{question}"},
            ],
        }
        request = Request(self.url, data=json.dumps(payload).encode(), method="POST")
        request.add_header("Content-Type", "application/json")
        if self.api_key:
            request.add_header("Authorization", f"Bearer {self.api_key}")
        with urlopen(request, timeout=60) as response:
            data = json.loads(response.read())
        return data["choices"][0]["message"]["content"]
