import frappe


def get_context(context):
    context.no_cache = 1
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/manage"
        raise frappe.Redirect

    name = frappe.form_dict.get("name")
    if not name:
        frappe.local.flags.redirect_location = "/manage"
        raise frappe.Redirect

    art = frappe.db.get_value(
        "Artwork",
        name,
        ["name", "title", "image", "medium", "year", "description", "for_sale", "price", "is_published"],
        as_dict=True,
    )
    if not art:
        frappe.local.flags.redirect_location = "/manage"
        raise frappe.Redirect

    context.art = art
    context.title = "Edit — " + art.title
