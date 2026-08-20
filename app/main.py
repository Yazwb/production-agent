#shoudown,startup
from contextlib import asynccontextmanager
import logging
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.router import router
from app.core.config import get_settings
from app.core.container import get_container
from app.core.logging import configure_logging


logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(_: FastAPI):
    # 配置日志
    configure_logging()
    logger.info("Application startup")
    # 初始化依赖注入容器
    get_container()
    yield
    logger.info("Application shutdown")
    #你好
    #await close_redis()
    #await close_milvus()
    #await close_http_client()

# 读取配置对象
settings = get_settings()
#创建FastAPI应用实例
app = FastAPI(
    title=settings.app_name,
    #http://127.0.0.1:8000/docs
    version="0.1.0",
    #api版本
    lifespan=lifespan,
)

# MVP 阶段允许跨域，生产环境应限制为前端实际域名。
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    #allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
#注册后端接口
app.include_router(
    router,
    prefix=settings.api_prefix,
)

# 将静态页面挂在根路径，方便直接打开 Demo，不需要单独部署前端服务。
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).resolve().parent.parent / "static", html=True),
    name="static",
)
#路由先后顺序很重要，先注册API，在挂载静态页面，否则会导致静态页面无法访问。
