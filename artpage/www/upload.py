import frappe

from artpage.utils import get_currency_symbol


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/upload"
        raise frappe.Redirect
    if not frappe.has_permission("Artwork", "create"):
        frappe.throw("You are not permitted to upload artworks.", frappe.PermissionError)
    context.currency_symbol = get_currency_symbol()
