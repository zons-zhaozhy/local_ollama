from fastapi import FastAPI, HTTPException, File, UploadFile, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import logging
from fastapi.responses import StreamingResponse
import httpx
from urllib.parse import urljoin, urlparse, urlunparse
from httpx import AsyncClient, ReadTimeout, ConnectTimeout
import json
import uvicorn
import ssl
import tempfile
import os
import whisper
import ffmpeg  # 添加此行以导入 ffmpeg 库
from typing import Optional

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


app = FastAPI()

# 添加 CORS 中间件
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 提供静态文件
app.mount("/static", StaticFiles(directory="static"), name="static")

# 定义请求体的模型
class GenerateRequest(BaseModel):
    baseUrl: str
    model: str
    prompt: str
    fileContent: Optional[str] = None  # 修改 fileContent 字段

@app.post("/generate")
async def generate(request: GenerateRequest):
    logging.info(f"接收到生成请求，模型: {request.model}")
    logging.info(f"问题: {request.prompt}")
    
    try:
        parsed_url = urlparse(request.baseUrl)
        if not parsed_url.scheme:
            parsed_url = parsed_url._replace(scheme="http")
        api_url = urlunparse(parsed_url._replace(path="/api/generate"))
        
        logging.info(f"调用 Ollama API: {api_url}")

        prompt = request.prompt
        if request.fileContent:
            prompt += f"\n\n文件内容:\n{request.fileContent}"

        async def stream_response():
            async with AsyncClient(timeout=120.0, verify=False) as client:  # 增加超时时间
                response = await client.post(api_url, json={"model": request.model, "prompt": prompt})
                response.raise_for_status()
                logging.info("成功调用 Ollama API，开始流式传输响应")
                
                # 读取响应内容并记录日志
                async for chunk in response.aiter_bytes():
                    logging.info(f"接收到的响应块: {chunk.decode('utf-8')}")
                    yield chunk

        return StreamingResponse(stream_response(), media_type='application/json')
    
    except httpx.RequestError as e:
        logging.error(f"请求过程中发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"请求错误: {str(e)}")
    except httpx.HTTPStatusError as e:
        logging.error(f"服务器返回错误: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"服务器错误: {str(e)}")
    except Exception as err:
        logging.error(f"发生错误: {err}")
        raise HTTPException(status_code=500, detail=f"服务器错误，发生异常: {str(err)}")

@app.get("/api/tags")
async def get_tags(base_url: str):
    try:
        if not base_url.endswith('/'):
            base_url += '/'
        
        parsed_url = urlparse(base_url)
        parsed_url = parsed_url._replace(scheme="http")  # 强制使用 HTTP
        tags_url = urlunparse(parsed_url._replace(path="api/tags"))
        logging.info(f"请求 URL: {tags_url}")  # 添加日志
        
        async with httpx.AsyncClient(verify=False) as client:
            response = await client.get(tags_url, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            logging.info(f"成功获取模型列表: {data}")
            # 确保返回的数据是一个包含模型名称的数组
            models = [model['name'] for model in data['models']]
            return {"models": models}
    except httpx.RequestError as e:
        logging.error(f"请求模型列表时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"无法获取模型列表: {str(e)}")
    except httpx.HTTPStatusError as e:
        logging.error(f"获取模型列表时服务器返回错误: {e.response.status_code}")
        raise HTTPException(status_code=e.response.status_code, detail=f"获取模型列表失败: {str(e)}")
    except Exception as e:
        logging.error(f"未知错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"未知错误: {str(e)}")

@app.get("/")
async def read_root():
    return {"message": "欢迎访问模型问答系统，请访问 /static/index.html 查看页面。"}

@app.post("/api/speech_to_text")
async def speech_to_text(request: Request, audio: UploadFile = File(...)):
    try:
        content = await audio.read()
        logging.info(f"上传文件大小: {len(content)} 字节")  # 添加日志记录文件大小
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_audio:
            temp_audio.write(content)
            temp_audio_path = temp_audio.name

        # 将 .webm 文件转换为 .wav 文件
        wav_path = temp_audio_path.replace(".webm", ".wav")
        ffmpeg.input(temp_audio_path).output(wav_path).run()

        # 使用 OpenAI Whisper 进行语音识别
        model = whisper.load_model("base")
        result = model.transcribe(wav_path, language="zh")

        text = result["text"]
        logging.info(f"识别到的文本: {text}")  # 添加日志记录识别到的文本
        
        return {"text": text}
    
    except Exception as e:
        logging.error(f"处理音频时发生错误: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
    finally:
        if 'temp_audio_path' in locals():
            try:
                os.unlink(temp_audio_path)
            except PermissionError:
                logging.warning(f"无法删除文件: {temp_audio_path}")
        if 'wav_path' in locals():
            try:
                os.unlink(wav_path)
            except PermissionError:
                logging.warning(f"无法删除文件: {wav_path}")

# 考虑添加一个健康检查端点
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    import debugpy

    # 启用调试器
    debugpy.listen(("0.0.0.0", 5678))
    print("等待调试器连接...")
    debugpy.wait_for_client()
    print("调试器已连接")

    # 启动应用
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8443,
        reload=True
    )