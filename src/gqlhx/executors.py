from typing import Any, Dict, Optional, Tuple

class GraphQLExecutionError(Exception):
    pass

def execute_graphql(schema: Any, query: str,
                    variables: Optional[Dict]=None,
                    operation_name: Optional[str]=None) -> Tuple[Dict, list]:
    variables = variables or None
    if hasattr(schema, "execute_sync"):
        res = schema.execute_sync(query, variable_values=variables, operation_name=operation_name)
        return getattr(res,'data',{}) or {}, getattr(res,'errors',[]) or []
    if hasattr(schema, "execute"):
        res = schema.execute(query, variable_values=variables, operation_name=operation_name)
        return getattr(res,'data',{}) or {}, getattr(res,'errors',[]) or []
    if callable(schema):
        res = schema(query, variables=variables, operation_name=operation_name)
        if isinstance(res, tuple) and len(res)==2: return res
        if isinstance(res, dict): return res, []
    raise GraphQLExecutionError("Unsupported schema/executor")