"""LLM 模型管理 API"""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from app.services.llm_service import llm_service
from app.core.auth import get_current_user
from app.models.user import User

router = APIRouter()


class ModelInfo(BaseModel):
    """模型信息"""
    name: str
    display_name: str
    description: str
    parameters: str
    context_length: int


class SwitchModelRequest(BaseModel):
    """切换模型请求"""
    model_name: str = Field(..., description="模型名称")


class AvailableModelsResponse(BaseModel):
    """可用模型列表响应"""
    models: List[ModelInfo]
    current_model: str


# 预定义模型列表
AVAILABLE_MODELS = [
    ModelInfo(
        name="qwen2.5:3b",
        display_name="Qwen 2.5 3B",
        description="轻量级中文友好模型，适合一般问答",
        parameters="3B",
        context_length=4096
    ),
    ModelInfo(
        name="qwen2.5:7b",
        display_name="Qwen 2.5 7B",
        description="中等规模模型，更好的推理能力",
        parameters="7B",
        context_length=8192
    ),
    ModelInfo(
        name="phi3:mini",
        display_name="Phi-3 Mini",
        description="微软轻量模型，速度快",
        parameters="3.8B",
        context_length=4096
    ),
    ModelInfo(
        name="llama3.2:3b",
        display_name="Llama 3.2 3B",
        description="Meta 最新轻量模型",
        parameters="3B",
        context_length=4096
    ),
]


@router.get("/models", response_model=AvailableModelsResponse, summary="获取可用模型列表")
async def get_available_models(
    current_user: User = Depends(get_current_user)
):
    """获取 Ollama 可用模型列表"""
    try:
        # 获取 Ollama 实际可用模型
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{llm_service.base_url}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                ollama_model_names = [m["name"] for m in ollama_models]
            else:
                ollama_model_names = []
    except Exception:
        ollama_model_names = []
    
    # 过滤出实际可用的模型
    available = [m for m in AVAILABLE_MODELS if m.name in ollama_model_names]
    
    return AvailableModelsResponse(
        models=available,
        current_model=llm_service.model
    )


@router.post("/switch", summary="切换当前模型")
async def switch_model(
    request: SwitchModelRequest,
    current_user: User = Depends(get_current_user)
):
    """切换到指定模型"""
    # 验证模型是否可用
    model_names = [m.name for m in AVAILABLE_MODELS]
    if request.model_name not in model_names:
        raise HTTPException(status_code=400, detail=f"Model {request.model_name} not found")
    
    try:
        # 检查模型是否已拉取
        import httpx
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{llm_service.base_url}/api/tags")
            if response.status_code == 200:
                ollama_models = response.json().get("models", [])
                ollama_model_names = [m["name"] for m in ollama_models]
                
                if request.model_name not in ollama_model_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Model {request.model_name} not pulled. Please pull it first."
                    )
    except HTTPException:
        raise
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to check model availability")
    
    # 切换模型
    llm_service.model = request.model_name
    
    return {
        "message": f"Switched to {request.model_name}",
        "current_model": llm_service.model
    }
