import frappe

from artpage.utils import with_cache_buster


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/manage"
        raise frappe.Redirect
    if not frappe.has_permission("Artwork", "write"):
        frappe.throw("You are not permitted to manage artworks.", frappe.PermissionError)

    artworks = frappe.db.get_all(
        "Artwork",
        fields=["name", "title", "image", "medium", "is_published", "creation", "modified"],
        order_by="creation desc",
        ignore_permissions=True,
    )
    for art in artworks:
        art.image = with_cache_buster(art.image, art.modified)
    context.artworks = artworks
    context.title = "Manage Artworks"
