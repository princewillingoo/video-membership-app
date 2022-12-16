# import uuid
# from typing import Optional
# from starlette.exceptions import HTTPException

from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse

from app import utils
from app.users.decorators import login_required
from app.shortcuts import ( get_object_or_404, render, redirect)
from app.videos.schemas import VidoeCreateSchema#,  get_object_or_404, is_htmx )

from app.watch_events.models import WatchEvent
from .models import Video
# from .schemas import ( VideoCreateSchema, VideoEditSchema)


router = APIRouter(
    prefix='/videos'
)

@router.get("/create", response_class=HTMLResponse)
@login_required
def video_create_view(request: Request):
    return render(request, "videos/create.html", {})

@router.post("/create", response_class=HTMLResponse)
@login_required
def video_create_post_view(request: Request, url: str = Form(...), title: str = Form(...)):
    
    raw_data = {
        "title":title,
        "url":url,
        "user_id": request.user.username 
        
    }
    data, errors = utils.valid_schema_data_or_error(raw_data, VidoeCreateSchema)
    context = {
        "data": data,
        "errors": errors,
        "url": url,
    }
    if len(errors) > 0:
        return render(request, "videos/create.html", context, status_code=400)
    redirect_path = data.get('path') or "/videos/create" 
    return redirect(redirect_path)

@router.get("/", response_class=HTMLResponse)
def video_list_view(request: Request):
    q = Video.objects.all().limit(100)
    context = {
        "object_list": q
    }
    return render(request, "videos/list.html", context)

@router.get("/{host_id}", response_class=HTMLResponse)
def video_detail_view(request: Request, host_id:str):
    obj = get_object_or_404(Video, host_id=host_id)
    start_time = 0
    if request.user.is_authenticated:
        user_id = request.user.username
        start_time = WatchEvent.get_resume_time(host_id, user_id)
    context = {
        "host_id": host_id,
        "object": obj,
        "start_time": start_time  
    }
    return render(request, "videos/detail.html", context)