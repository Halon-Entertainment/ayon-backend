from datetime import datetime
from typing import Any

import strawberry


@strawberry.type
class KanbanNode:
    project_name: str = strawberry.field()
    project_code: str = strawberry.field()
    id: str = strawberry.field()
    name: str = strawberry.field()
    label: str | None = strawberry.field()
    status: str = strawberry.field()
    tags: list[str] = strawberry.field()
    task_type: str = strawberry.field()
    assignees: list[str] = strawberry.field()
    updated_at: datetime = strawberry.field()
    created_at: datetime = strawberry.field()
    due_date: datetime | None = strawberry.field(default=None)
    folder_id: str = strawberry.field()
    folder_name: str = strawberry.field()
    folder_label: str | None = strawberry.field()
    folder_path: str = strawberry.field()
    thumbnail_id: str | None = strawberry.field(default=None)
    last_version_with_thumbnail_id: str | None = strawberry.field(default=None)


def kanban_node_from_record(
    project_name: str | None,
    record: dict[str, Any],
    context: dict[str, Any],
) -> KanbanNode:
    record = dict(record)
    record.pop("cursor", None)

    project_name = record.pop("project_name", project_name)
    assert project_name, "project_name is required"

    due_date = record.pop("due_date", None)
    if isinstance(due_date, datetime):
        due_date = due_date.replace(tzinfo=None)
    elif isinstance(due_date, str):
        due_date = datetime.fromisoformat(due_date)
    record["due_date"] = due_date

    return KanbanNode(
        project_name=project_name,
        **record,
    )


KanbanNode.from_record = staticmethod(kanban_node_from_record)  # type: ignore
