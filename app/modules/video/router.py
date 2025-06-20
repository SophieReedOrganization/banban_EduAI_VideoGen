from fastapi import APIRouter, BackgroundTasks
from datetime import datetime, timezone
from app.core import MongoDB, Config
from app.middleware import CustomJSONResponse
from .schema import VideoGenerationRequest
from .service import process_generate_educational_video,identify_keyword

router = APIRouter(prefix="/video", tags=["video"])

@router.post("/generate/{client_id}")
async def generate_educational_video(
    background_tasks: BackgroundTasks,
    client_id: str,
    request_data: VideoGenerationRequest,
):
    region = "openql"
    task_id = f"video_{client_id}_{int(datetime.now().timestamp())}"

    # 步驟0：關鍵字辨識，如果找到關鍵字直接返回對應的 URL
    if request_data.content:
        keyword_url = await identify_keyword(request_data.content)
        if keyword_url:
            # 如果找到關鍵字，直接返回預設的任務資料和 URL
            task_data = {
                "client_id": client_id,
                "task_id": task_id,
                "status": "success",
                "metadata": {
                    "text": request_data.text,
                    "image_base64": request_data.image_base64 is not None,
                    "content": request_data.content is not None,
                    "keyword_matched": True
                },
                "gcs_public_url": keyword_url,
                "video_list_url": f"https://{Config.APP_NAME}-{Config.PROJECT_NUMBER}.{Config.REGION}.run.app/video/tasks/{client_id}",
                "created_at": datetime.now(timezone.utc)
            }
            
            return CustomJSONResponse(content={"data": task_data})
    
    # 如果沒有找到關鍵字，繼續原本的後台任務流程
    background_tasks.add_task(
        process_generate_educational_video,
        region,
        client_id,
        task_id,
        request_data.text, 
        request_data.voice,
        request_data.image_base64,
        request_data.content

    )
    gcs_public_url = f"https://storage.googleapis.com/generate_educational_video/{region}/{client_id}/{task_id}.mp4"
    video_list_url = f"https://{Config.APP_NAME}-{Config.PROJECT_NUMBER}.{Config.REGION}.run.app/video/tasks/{client_id}"

    task_data = {
        "client_id": client_id,
        "task_id": task_id,
        "status": "processing",
        "metadata": {
            "text": request_data.text,
            "image_base64": request_data.image_base64 is not None,
            "content": request_data.content is not None
        },
        "gcs_public_url": gcs_public_url,
        "video_list_url": video_list_url,
        "created_at": datetime.now(timezone.utc)
    }
    
    await MongoDB.upsert_one(f"{region.title()}Video", {'task_id': task_id}, {"$set": task_data})
    return CustomJSONResponse(content={"data": task_data})

@router.get("/tasks/{client_id}")
async def get_video_tasks(
    client_id: str
):
    region = "openql"
    pipeline = [
        {"$match": {"client_id": client_id}},
        {"$sort": {"created_at": -1}}
    ]
    task_data = await MongoDB.get_many(f"{region.title()}Video", pipeline)
    return CustomJSONResponse(content={"data": task_data})

@router.get("/tasks/{client_id}/{task_id}")
async def get_video_task(
    client_id: str,
    task_id: str
):
    region = "openql"
    task_data = await MongoDB.get_one(f"{region.title()}Video", {"task_id": task_id})
    if not task_data:
        return CustomJSONResponse(content={"error": "Task not found"}, status_code=404)
    return CustomJSONResponse(content={"data": task_data})

@router.delete("/tasks/{client_id}/{task_id}")
async def delete_video_task(
    client_id: str,
    task_id: str
):
    region = "openql"
    await MongoDB.delete_one(f"{region.title()}Video", {"task_id": task_id})
    return CustomJSONResponse(content={"message": "Task deleted successfully"})

@router.delete("/tasks/{client_id}")
async def delete_all_video_tasks(
    client_id: str
):
    region = "openql"
    await MongoDB.delete_many(f"{region.title()}Video", {"client_id": client_id})
    return CustomJSONResponse(content={"message": "All tasks deleted successfully"})