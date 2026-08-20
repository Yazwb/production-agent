# 用于清理文本
import logging
import re
# 为每个文本块生成唯一ID
from uuid import uuid4

from app.domain.models import Chunk, ParsedPage


logger = logging.getLogger(__name__)


class TextChunker:
    """按照固定窗口切分文本，并保留相邻窗口的重叠"""
    def __init__(self, chunk_size: int = 800, overlap: int = 100) -> None:
            self.chunk_size = chunk_size
            self.overlap = overlap

    def split(self, document_id: str, filename: str, pages: list[ParsedPage]) -> list[Chunk]:
                chunks: list[Chunk] = []
                position = 0
                for page in pages:
                      text = self._clean(page.text)
                      start = 0
                      while start < len(text):
                             end = min(len(text), start + self.chunk_size)
                             chunks.append(
                                    Chunk(
                                           str(uuid4()),
                                           document_id,
                                           filename,
                                           page.page_number,
                                           position,
                                           text[start: end],
                                    )
                             )
                             position += 1
                             if end >= len(text):
                                    break
                             #保留前一段结尾，留有重叠
                             start = max(start + 1, end - self.overlap)
                logger.info("Chunked document %s: %d chunks", filename, len(chunks))
                return chunks
    

    @staticmethod
    def _clean(text: str) -> str:
           text = re.sub(r"[\t\r ]+", " ", text)
           return re.sub(r"\n{3,}", "\n\n", text).strip()
