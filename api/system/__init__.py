from fastapi import APIRouter, Depends, Response
from nxtools import logging

from openpype.api import dep_current_user
from openpype.entities import UserEntity
from openpype.events import dispatch_event

router = APIRouter(
    prefix="/system",
    tags=["System"],
)


@router.post("/restart", response_class=Response)
async def request_server_restart(user: UserEntity = Depends(dep_current_user)):
    logging.info("Dispatching event restart request", user=user.name)
    await dispatch_event("server.restart_requested", user=user.name)
    return Response(status_code=204)