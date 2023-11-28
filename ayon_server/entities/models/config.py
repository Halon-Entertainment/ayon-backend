"""Entity model config."""


def camelize(src: str) -> str:
    """Convert snake_case to camelCase."""
    components = src.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


class EntityModelConfig:
    """Entity model config."""

    populate_by_name = True
    alias_generator = camelize
    # json_loads = json_loads
    # json_dumps = json_dumps
