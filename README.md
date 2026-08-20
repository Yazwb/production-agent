# 工业智能知识问答 MVP

这是一个可以真正跑起来的第一版：上传工业 PDF/Word/TXT，建立知识库，提问后返回相关资料和引用页码。

```text
文档上传 -> 文档解析 -> 文本切块 -> SQLite FTS5 检索 -> 回答 -> 引用来源
```

默认不要求下载模型：未设置 `INDUSTRIAL_AI_LLM_BASE_URL` 时，系统使用本地抽取式回答；接入 Qwen/vLLM 等 OpenAI-compatible 服务后，自动切换为大模型回答。

## 1. 安装与启动

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

浏览器打开 `http://127.0.0.1:8000`，API 文档在 `http://127.0.0.1:8000/docs`。

## 2. 使用示例 PDF

仓库根目录已经放入一份热风烘干设备技术文档。启动后在页面左侧上传它，选择“设备”，然后提问：

```text
热风烘干设备温度过高应该如何排查？
设备运行时出现振动，应该检查哪些部件？
```

## 3. API 调用

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/v1/documents/upload -F "file=@工业简易技术文档（热风烘干设备 三套案例）.pdf" -F "domain=equipment"
curl.exe -X POST http://127.0.0.1:8000/api/v1/chat -H "Content-Type: application/json" -d '{"question":"设备温度过高怎么处理？","domain":"auto"}'
```

## 4. 代码如何对应业务

- `app/rag/parser.py`：PDF、Word、TXT 解析，并保留页码
- `app/rag/chunking.py`：按字符窗口切块
- `app/infrastructure/repositories/sqlite.py`：文档、Chunk 持久化和 FTS5 检索
- `app/rag/retriever.py`：召回 TopK
- `app/agents/router.py`：自动判断工艺、设备、质量领域
- `app/agents/orchestrator.py`：调用领域 Agent
- `app/infrastructure/llm/vllm.py`：本地抽取式回答或 OpenAI-compatible 模型
- `app/api/routes/`：上传、文档列表、删除、问答接口
- `static/index.html`：最小可用前端

## 5. 接入真实模型

复制 `.env.example` 为 `.env`，配置：

```env
INDUSTRIAL_AI_LLM_BASE_URL=http://localhost:8000/v1
INDUSTRIAL_AI_LLM_API_KEY=your-key
INDUSTRIAL_AI_LLM_MODEL=Qwen3-14B
```

下一步再做 BGE-M3、Milvus、BM25 + RRF、BGE-Reranker、Badcase 评测、Redis 会话和 LangGraph 多 Agent。不要在 MVP 阶段同时引入这些组件。
