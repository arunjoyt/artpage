import frappe

from artpage.utils import get_currency_symbol, with_cache_buster


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/manage"
        raise frappe.Redirect
    if not frappe.has_permission("Artwork", "write"):
        frappe.throw("You are not permitted to edit artworks.", frappe.PermissionError)

    name = frappe.form_dict.get("name")
    if not name:
        frappe.local.flags.redirect_location = "/manage"
        raise frappe.Redirect

    art = frappe.db.get_value(
        "Artwork",
        name,
        ["name", "title", "image", "medium", "year", "description", "for_sale", "price", "is_published", "modified"],
        as_dict=True,
    )
    if not art:
        frappe.local.flags.redirect_location = "/manage"
        raise frappe.Redirect

    art.image = with_cache_buster(art.image, art.modified)
    context.art = art
    context.title = "Edit — " + art.title
    context.currency_symbol = get_currency_symbol()
