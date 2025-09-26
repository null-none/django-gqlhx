# django-gqlhx

Server-rendered GraphQL → HTMX bridge for Django

---

## Install

```bash
pip install django-gqlhx
```

Your Django settings:

```python
INSTALLED_APPS = [
    # ...
    "gqlhx",
    "core",     # your app with GraphQL schema
]

# Point to your graphene schema object (dotted path)
GQLHX_SCHEMA = "core.schema.schema"
```

`urls.py`:

```python
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from gqlhx import GraphQLHTMXView

urlpatterns = [
    path("gql-html", csrf_exempt(GraphQLHTMXView.as_view()), name="gql_html"),
]
```

---

## HTMX usage

```html
<script src="https://unpkg.com/htmx.org@1.9.12"></script>

<script type="application/graphql" id="GQL_USER_LIST">
  query UserList($search: String, $limit: Int) {
    users(search: $search, limit: $limit) { id name email }
  }
</script>

<input id="q" placeholder="search"/>
<input id="limit" type="number" value="10"/>

<button
  hx-post="/gql-html"
  hx-target="#out"
  hx-swap="innerHTML"
  hx-vals='js:{
    query: document.getElementById("GQL_USER_LIST").textContent,
    variables: JSON.stringify({
      search: document.getElementById("q").value || null,
      limit: parseInt(document.getElementById("limit").value || "10")
    }),
    renderer: "partials/users_table.html"
  }'
>Load</button>

<div id="out"></div>
```

**CSRF**: add header in prod

```html
<script>
function getCookie(name){const m=document.cookie.match('(^|;)\s*'+name+'\s*=\s*([^;]+)');return m?m.pop():''}
document.addEventListener('htmx:configRequest', (e)=>{
  e.detail.headers['X-CSRFToken'] = getCookie('csrftoken');
});
</script>
```

---

## Subclassing

```python
# myapp/views.py
from gqlhx import GraphQLHTMXView

class MyGQLView(GraphQLHTMXView):
    RENDERERS = {
        "users.table": "partials/users_table.html",
        "users.cards": "partials/users_cards.html",
    }
    FALLBACK_TEMPLATE = "partials/users_table.html"  # override default if you want

    def build_context(self, data, root_key):
        ctx = super().build_context(data, root_key)
        ctx["powered_by"] = "django-gqlhx"
        return ctx
```

`urls.py`:

```python
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from myapp.views import MyGQLView

urlpatterns = [
    path("gql-html", csrf_exempt(MyGQLView.as_view()), name="gql_html"),
]
```
