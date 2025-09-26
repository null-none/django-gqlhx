from typing import Any, Dict, List, Optional
import json
from django.conf import settings
from django.http import HttpResponse, HttpResponseBadRequest
from django.template.loader import select_template
from django.template.response import TemplateResponse
from django.views.generic import View

try:
    from graphene_django.settings import graphene_settings  # optional
except Exception:
    graphene_settings = None

from .executors import execute_graphql
from .utils import import_string


class GraphQLHTMXView(View):
    """Universal GraphQL ↔ HTMX HTML bridge for Django."""

    SCHEMA: Any = None
    RENDERERS: Dict[str, str] = {}
    FALLBACK_TEMPLATE: str = "gqlhx/fallback.html"
    AUTO_CANDIDATES: List[str] = [
        "partials/{root}.html",
        "partials/{root}_table.html",
        "gqlhx/fallback.html",
    ]

    # ---- Hooks ----

    def get_schema(self) -> Any:
        schema = self.SCHEMA
        if isinstance(schema, str):
            return import_string(schema)
        if schema is not None:
            return schema

        dotted = getattr(settings, "GQLHX_SCHEMA", None)
        if dotted:
            return import_string(dotted)

        if graphene_settings and getattr(graphene_settings, "SCHEMA", None):
            return graphene_settings.SCHEMA

        raise RuntimeError(
            "No GraphQL schema configured. Set GraphQLHTMXView.SCHEMA, "
            "settings.GQLHX_SCHEMA, or configure graphene_django."
        )

    def execute(
        self,
        schema: Any,
        query: str,
        variables: Optional[Dict] = None,
        operation_name: Optional[str] = None,
    ) -> Dict:
        data, errors = execute_graphql(schema, query, variables, operation_name)
        return {"data": data, "errors": errors}

    def build_context(
        self, data: Dict[str, Any], root_key: Optional[str]
    ) -> Dict[str, Any]:
        ctx: Dict[str, Any] = {"gql": data}
        root = data.get(root_key) if root_key else None
        if root_key:
            ctx[root_key] = root
            ctx["root"] = root
            if isinstance(root, list):
                ctx["items"] = root
        return ctx

    def get_renderer_name(self, request) -> Optional[str]:
        return request.POST.get("renderer") or request.POST.get("tpl") or None

    def get_pick_key(self, request, data: Dict[str, Any]) -> Optional[str]:
        pick = request.POST.get("pick")
        if pick and pick in data:
            return pick
        keys = list(data.keys())
        return keys[0] if len(keys) == 1 else None

    def get_template(self, renderer: Optional[str], root_key: Optional[str]):
        candidates: List[str] = []
        if renderer:
            if renderer.endswith(".html"):
                candidates = [renderer]
            elif renderer in self.RENDERERS:
                candidates = [self.RENDERERS[renderer]]

        if not candidates and root_key:
            for pattern in self.AUTO_CANDIDATES:
                candidates.append(pattern.format(root=root_key))

        if self.FALLBACK_TEMPLATE not in candidates:
            candidates.append(self.FALLBACK_TEMPLATE)

        return select_template(candidates)

    # ---- Internals ----

    def _load_variables(self, raw: Optional[str]) -> Dict[str, Any]:
        if not raw:
            return {}
        try:
            return json.loads(raw)
        except Exception as ex:
            raise ValueError(f"Bad variables JSON: {ex}")

    # ---- HTTP ----

    def post(self, request, *args, **kwargs):
        query = request.POST.get("query")
        if not query:
            return HttpResponseBadRequest("Missing 'query'")

        try:
            variables = self._load_variables(request.POST.get("variables"))
        except ValueError as e:
            return HttpResponseBadRequest(str(e))

        operation_name = request.POST.get("operationName") or None
        renderer = self.get_renderer_name(request)

        schema = self.get_schema()
        result = self.execute(schema, query, variables, operation_name)
        errors = result.get("errors") or []
        if errors:
            tpl = select_template(["gqlhx/error.html"])
            return TemplateResponse(
                request, tpl.template.name, {"errors": errors}, status=400
            )

        data = result.get("data") or {}
        root_key = self.get_pick_key(request, data)
        context = self.build_context(data, root_key)

        template = self.get_template(renderer, root_key)
        return TemplateResponse(request, template.template.name, context)

    def get(self, request, *args, **kwargs):
        return HttpResponse("POST GraphQL to this endpoint.")
