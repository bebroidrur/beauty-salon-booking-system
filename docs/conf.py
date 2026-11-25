"""Build code docstrings and existing laboratory guides without source copies."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

project = "Онлайн-запис до салону краси"
author = "Навчальний проєкт"
release = "ЛР6"
language = "uk"
extensions = ["sphinx.ext.autodoc", "sphinx.ext.napoleon", "myst_parser"]
source_suffix = {".rst": "restructuredtext", ".md": "markdown"}
root_doc = "index"
include_patterns = [
    "index.rst",
    "python-api.rst",
    "user-guide.md",
    "lab4/resource-model.md",
    "lab4/schemas.md",
    "lab4/errors.md",
]
exclude_patterns = ["generated/**"]
autodoc_member_order = "bysource"
autodoc_default_options = {"members": True, "special-members": "__init__"}
autoclass_content = "class"
napoleon_google_docstring = True
napoleon_numpy_docstring = False
html_theme = "alabaster"
html_copy_source = False
html_show_sourcelink = False
html_last_updated_fmt = None
html_theme_options = {"show_powered_by": False}


def _fix_singlehtml_anchors(app, doctree, docname):
    """Normalize Sphinx 8.2 cross-document fragments in the merged page."""
    if app.builder.name != "singlehtml":
        return
    from docutils import nodes

    for node in doctree.findall(nodes.reference):
        uri = node.get("refuri", "")
        if uri.startswith("#document-") and uri.count("#") == 2:
            node["refuri"] = "#" + uri.rsplit("#", 1)[1]


def _singlehtml_context(app, pagename, templatename, context, doctree):
    """Omit theme links to index/search pages absent from singlehtml."""
    if app.builder.name == "singlehtml":
        hasdoc = context["hasdoc"]
        context["hasdoc"] = lambda name: (
            name not in {"genindex", "search"} and hasdoc(name)
        )


def setup(app):
    """Apply presentation fixes without editing generated HTML by hand."""
    app.connect("doctree-read", _namespace_section_ids, priority=400)
    app.connect("doctree-resolved", _fix_singlehtml_anchors)
    app.connect("html-page-context", _singlehtml_context)


def _namespace_section_ids(app, doctree):
    """Keep automatic heading IDs unique when Ukrainian pages are merged."""
    from docutils import nodes

    prefix = app.env.docname.replace("/", "-") + "--"
    renamed = {}
    for section in doctree.findall(nodes.section):
        for ident in section["ids"]:
            if not ident.startswith("module-"):
                renamed[ident] = prefix + ident
        section["ids"] = [
            renamed.get(ident, ident) for ident in section["ids"]
        ]
    for old, new in renamed.items():
        if old in doctree.ids:
            doctree.ids[new] = doctree.ids.pop(old)
    for name, ident in doctree.nameids.items():
        doctree.nameids[name] = renamed.get(ident, ident)
    for node in doctree.findall(nodes.Element):
        if node.get("refid") in renamed:
            node["refid"] = renamed[node["refid"]]
