from typing import Any, Dict, Optional, Tuple


class GraphQLExecutionError(Exception):
    pass


def execute_graphql(
    schema: Any,
    query: str,
    variables: Optional[Dict] = None,
    operation_name: Optional[str] = None,
) -> Tuple[Dict, list]:
    """Execute a GraphQL query against a schema (graphene or strawberry)."""
    variables = variables or None
    # Strawberry first (sync)
    if hasattr(schema, "execute_sync"):
        res = schema.execute_sync(
            query, variable_values=variables, operation_name=operation_name
        )
        data = getattr(res, "data", None) or {}
        errors = getattr(res, "errors", None) or []
        return data, errors
    # Graphene / generic execute
    if hasattr(schema, "execute"):
        res = schema.execute(
            query, variable_values=variables, operation_name=operation_name
        )
        data = getattr(res, "data", None) or {}
        errors = getattr(res, "errors", None) or []
        return data, errors
    # Callable schema fallback
    if callable(schema):
        res = schema(query, variables=variables, operation_name=operation_name)
        if isinstance(res, tuple) and len(res) == 2:
            return res
        if isinstance(res, dict):
            return res, []
    raise GraphQLExecutionError(
        "Unsupported schema/executor. Override get_schema()/execute()."
    )
