from typing import Any

from fastapi import Depends, Response
from nxtools import logging

from ayon_server.api.dependencies import dep_current_user, dep_event_id
from ayon_server.entities import UserEntity
from ayon_server.events import EventModel, dispatch_event, update_event
from ayon_server.exceptions import ForbiddenException, NotFoundException
from ayon_server.lib.postgres import Postgres
from ayon_server.types import NAME_REGEX, TOPIC_REGEX, Field, OPModel

from .router import router

#
# Models
#

normal_user_topic_whitelist: list[str] = []


class DispatchEventRequestModel(OPModel):
    topic: str = Field(
        ...,
        title="Topic",
        description="Topic of the event",
        example="log.info",
        regex=TOPIC_REGEX,
    )
    sender: str | None = Field(
        None,
        title="Sender",
        description="Identifier of the process that sent the event.",
    )
    hash: str | None = Field(
        None,
        title="Hash",
    )
    project: str | None = Field(
        None,
        title="Project name",
        description="Name of the project if the event belong to one.",
        example="MyProject",
        regex=NAME_REGEX,
    )
    depends_on: str | None = Field(
        None,
        title="Depends on",
        min_length=32,
        max_length=32,
    )
    description: str = Field(
        "",
        title="Description",
        description="Human-readable event description.",
    )
    summary: dict[str, Any] = Field(
        default_factory=dict,
        title="Summary",
        description="Arbitrary topic-specific data sent to clients in real time",
    )
    payload: dict[str, Any] = Field(
        default_factory=dict,
        title="Payload",
        description="Full event payload. Only avaiable in REST endpoint.",
    )
    finished: bool = Field(
        True,
        title="Finished",
        description="Is event finished (one shot event)",
        example=True,
    )
    store: bool = Field(
        True,
        title="Store",
        description="Set to False to not store one-shot event in database.",
        example=True,
    )


class UpdateEventRequestModel(OPModel):
    sender: str | None = None
    project_name: str | None = Field(
        None,
        title="Project name",
        deprecated="Deprecated use 'project' instead",
    )
    project: str | None = Field(None, title="Project name")
    status: str | None = None
    description: str | None = None
    summary: dict[str, Any] | None = None
    payload: dict[str, Any] | None = None


class DispatchEventResponseModel(OPModel):
    id: str = Field(
        ...,
        min_length=32,
        max_length=32,
        title="Event ID",
        description="ID of the created event.",
    )


#
# Endpoints
#


@router.post("/events", response_model=DispatchEventResponseModel)
async def post_event(
    request: DispatchEventRequestModel,
    user: UserEntity = Depends(dep_current_user),
) -> DispatchEventResponseModel:

    if not user.is_manager:
        if request.topic not in normal_user_topic_whitelist:
            raise ForbiddenException("Not allowed to update this event")

    event_id = await dispatch_event(
        request.topic,
        sender=request.sender,
        hash=request.hash,
        user=user.name,
        # TODO description
        description=request.description,
        summary=request.summary,
        payload=request.payload,
        finished=request.finished,
        store=request.store,
    )
    return DispatchEventResponseModel(id=event_id)


@router.get("/events/{event_id}")
async def get_event(
    user: UserEntity = Depends(dep_current_user),
    event_id: str = Depends(dep_event_id),
) -> EventModel:
    """Get event by ID.

    Return event data with given ID. If event is not found, 404 is returned.
    """

    query = "SELECT * FROM events WHERE id = $1", event_id

    if user.is_guest:
        raise ForbiddenException("Guests are not allowed to get events this way")

    event: EventModel | None = None
    async for record in Postgres.iterate(*query):
        event = EventModel(
            id=record["id"],
            hash=record["hash"],
            topic=record["topic"],
            project=record["project_name"],
            user=record["user_name"],
            sender=record["sender"],
            depends_on=record["depends_on"],
            status=record["status"],
            retries=record["retries"],
            description=record["description"],
            payload=record["payload"],
            summary=record["summary"],
            created_at=record["created_at"],
            updated_at=record["updated_at"],
        )
        break

    if event is None:
        raise NotFoundException("Event not found")
    return event


@router.patch("/events/{event_id}", response_class=Response)
async def update_existing_event(
    payload: UpdateEventRequestModel,
    user: UserEntity = Depends(dep_current_user),
    event_id: str = Depends(dep_event_id),
):
    """Update existing event."""

    if not user.is_manager:
        if payload.topic not in normal_user_topic_whitelist:
            raise ForbiddenException("Not allowed to update this event")

    if payload.project_name:
        logging.warning(
            "Patching event with projectName is deprecated. Use 'project' instead."
        )
    await update_event(
        event_id,
        payload.sender,
        payload.project_name or payload.project,
        payload.status,
        payload.description,
        payload.summary,
        payload.payload,
    )

    return Response(status_code=204)
