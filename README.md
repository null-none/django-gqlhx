
# django-gqlhx

Server-rendered GraphQL ↔ HTMX bridge for Django.

Front-end sends only two fields via `hx-vals`: 

**`query`** (GraphQL with inline args) and

**`renderer`** (template path or named renderer). The generic view executes your schema and returns an HTML fragment for instant htmx swaps.

#### Example

```html
<button
  hx-post="/gql-html"
  hx-target="#out"
  hx-swap="innerHTML"
  hx-vals='js:{
    query: `{ users(limit: 5) { id name email } }`,
    renderer: "partials/users_table.html"
  }'
>Load</button>
<div id="out"></div>
```

Django:
```python
# settings.py
INSTALLED_APPS += ["gqlhx"]
GQLHX_SCHEMA = "core.schema.schema"   # dotted path to your GraphQL schema object

# urls.py
from django.urls import path
from django.views.decorators.csrf import csrf_exempt
from gqlhx import GraphQLHTMXView

urlpatterns = [ path("gql-html", csrf_exempt(GraphQLHTMXView.as_view())) ]
```


#### Installation

Clone or add as a submodule, then install editable:

```bash
pip install -e .
```

> When published to PyPI: `pip install django-gqlhx`

---

--- Minimal HTMX Usage (only `query` + `renderer`)

Static query:

```html
<button
  hx-post="/gql-html"
  hx-target="#out"
  hx-swap="innerHTML"
  hx-vals='js:{
    query: `{ users(limit: 5) { id name email } }`,
    renderer: "partials/users_table.html"
  }'
>Table</button>
```

Dynamic query (safe interpolation with `JSON.stringify`):

```html
<input id="q" placeholder="search">
<input id="limit" type="number" value="10">

<button
  hx-post="/gql-html"
  hx-target="#out"
  hx-swap="innerHTML"
  hx-vals='js:{
    query: `{
      users(
        search: ${JSON.stringify(document.getElementById("q").value || null)},
        limit: ${parseInt(document.getElementById("limit").value || "10")}
      ){ id name email }
    }`,
    renderer: "partials/users_cards.html"
  }'
>Search</button>
```

#### License

MIT
