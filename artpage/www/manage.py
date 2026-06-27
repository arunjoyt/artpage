import frappe


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/manage"
        raise frappe.Redirect

    artworks = frappe.db.get_all(
        "Artwork",
        fields=["name", "title", "image", "medium", "is_published", "creation"],
        order_by="creation desc",
        ignore_permissions=True,
    )
    context.artworks = artworks
    context.title = "Manage Artworks"
