from fastapi import Depends, Response
from nxtools import log_traceback
from pydantic import BaseModel

from openpype.access.utils import folder_access_list
from openpype.api import (
    APIException,
    ResponseFactory,
    dep_current_user,
    dep_folder_id,
    dep_project_name,
)
from openpype.entities import FolderEntity, ProjectEntity, UserEntity
from openpype.exceptions import (
    ConstraintViolationException,
    ForbiddenException,
    RecordNotFoundException,
)
from openpype.lib.postgres import Postgres
from openpype.utils import EntityID

from .router import router

#
# [GET]
#


@router.get(
    "/projects/{project_name}/folders/{folder_id}",
    response_model=FolderEntity.model.main_model,
    responses={404: ResponseFactory.error(404, "Project not found")},
)
async def get_folder(
    user: UserEntity = Depends(dep_current_user),
    project_name: str = Depends(dep_project_name),
    folder_id: str = Depends(dep_folder_id),
):
    """Retrieve a folder by its ID."""

    try:
        folder = await FolderEntity.load(project_name, folder_id)
    except RecordNotFoundException:
        raise APIException(404, "Folder not found")
    except Exception:
        log_traceback("Unable to load folder")
        raise APIException(500, "Unable to load folder")

    try:
        access_list = await folder_access_list(user, project_name, "read")
    except ForbiddenException:
        raise APIException(403)

    if access_list is not None:
        if folder.path not in access_list:
            raise APIException(403)

    return folder.payload


#
# [POST]
#


class PostFolderResponseModel(BaseModel):
    id: str = EntityID.field("folder")


@router.post(
    "/projects/{project_name}/folders",
    status_code=201,
    response_model=PostFolderResponseModel,
    responses={
        409: ResponseFactory.error(409, "Coflict"),
    },
)
async def create_folder(
    post_data: FolderEntity.model.post_model,
    user: UserEntity = Depends(dep_current_user),
    project_name: str = Depends(dep_project_name),
):
    """Create a new folder.

    Use a POST request to create a new folder (with a new id).
    """

    project = await ProjectEntity.load(project_name)
    if not user.can("modify", project):
        raise APIException(403, "You are not allowed to modify this project")

    folder = FolderEntity(project_name=project_name, **post_data.dict())
    try:
        await folder.save()
    except ConstraintViolationException as e:
        raise APIException(409, f"Unable to create folder. {e.detail}")
    return PostFolderResponseModel(id=folder.id)


#
# [PATCH]
#


@router.patch(
    "/projects/{project_name}/folders/{folder_id}",
    status_code=204,
    response_class=Response,
)
async def update_folder(
    post_data: FolderEntity.model.patch_model,
    user: UserEntity = Depends(dep_current_user),
    project_name: str = Depends(dep_project_name),
    folder_id: str = Depends(dep_folder_id),
):
    """Patch (partially update) a folder."""

    async with Postgres.acquire() as conn:
        async with conn.transaction():
            try:
                folder = await FolderEntity.load(
                    project_name, folder_id, transaction=conn, for_update=True
                )
            except RecordNotFoundException:
                raise APIException(404, "Folder not found")

            try:
                access_list = await folder_access_list(user, project_name, "write")
            except ForbiddenException:
                raise APIException(403)

            if access_list is not None:
                if folder.path not in access_list:
                    raise APIException(403)

            folder.patch(post_data)

            try:
                await folder.save(transaction=conn)
            except ConstraintViolationException as e:
                raise APIException(409, f"Unable to update folder. {e.detail}")

    return Response(status_code=204)


#
# [DELETE]
#


@router.delete(
    "/projects/{project_name}/folders/{folder_id}",
    response_class=Response,
    status_code=204,
)
async def delete_folder(
    user: UserEntity = Depends(dep_current_user),
    project_name: str = Depends(dep_project_name),
    folder_id: str = Depends(dep_folder_id),
):
    """Delete a folder."""

    try:
        folder = await FolderEntity.load(project_name, folder_id)
    except RecordNotFoundException:
        raise APIException(404, "Folder not found")

    try:
        access_list = await folder_access_list(user, project_name, "write")
    except ForbiddenException:
        raise APIException(403)

    if access_list is not None:
        if folder.path not in access_list:
            raise APIException(403)

    await folder.delete()
    return Response(status_code=204)
