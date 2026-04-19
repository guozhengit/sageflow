"""文档处理服务 - 解析、分块、索引"""
import os
import uuid
from typing import List, Dict, Any
from pathlib import Path

import fitz  # PyMuPDF
from docx import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.core.config import get_settings
from app.services.embedding import embedding_service
from app.services.vector_store import vector_store

settings = get_settings()


class DocumentProcessor:
    """文档处理器"""
    
    def __init__(self):
        self.upload_dir = Path(settings.UPLOAD_DIR)
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        
        # 文本分块器
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=500,
            chunk_overlap=50,
            separators=["\n\n", "\n", "。", "！", "？", " ", ""]
        )
    
    async def process_file(
        self, 
        file_path: str, 
        file_name: str,
        user_id: str = "demo_user"
    ) -> Dict[str, Any]:
        """处理文件"""
        
        # 1. 提取文本
        text_content = await self._extract_text(file_path)
        
        # 2. 文本分块
        chunks = self._chunk_text(text_content)
        
        # 3. 向量化
        vectors = await embedding_service.encode_batch(chunks)
        
        # 4. 构建文档元数据
        documents = [
            {
                "document_name": file_name,
                "document_id": str(uuid.uuid4()),
                "user_id": user_id,
                "content": chunk,
                "page": i + 1,
                "chunk_index": i
            }
            for i, chunk in enumerate(chunks)
        ]
        
        # 5. 存储到向量数据库
        ids = await vector_store.add_vectors(vectors, documents)
        
        return {
            "document_id": documents[0]["document_id"],
            "document_name": file_name,
            "chunks_count": len(chunks),
            "vector_ids": ids
        }
    
    async def _extract_text(self, file_path: str) -> str:
        """提取文件文本"""
        ext = Path(file_path).suffix.lower()
        
        if ext == ".pdf":
            return self._extract_pdf(file_path)
        elif ext in [".doc", ".docx"]:
            return self._extract_docx(file_path)
        elif ext == ".txt":
            return self._extract_txt(file_path)
        else:
            raise ValueError(f"Unsupported file type: {ext}")
    
    def _extract_pdf(self, file_path: str) -> str:
        """提取 PDF 文本"""
        doc = fitz.open(file_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    
    def _extract_docx(self, file_path: str) -> str:
        """提取 DOCX 文本"""
        doc = Document(file_path)
        return "\n".join([para.text for para in doc.paragraphs])
    
    def _extract_txt(self, file_path: str) -> str:
        """提取 TXT 文本"""
        with open(file_path, "r", encoding="utf-8") as f:
            return f.read()
    
    def _chunk_text(self, text: str) -> List[str]:
        """文本分块"""
        return self.text_splitter.split_text(text)


# 全局单例
document_processor = DocumentProcessor()
