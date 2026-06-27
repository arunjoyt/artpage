import frappe


def get_context(context):
    context.no_cache = 1
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw("Artwork not found", frappe.DoesNotExistError)

    art = frappe.db.get_value(
        "Artwork",
        {"name": name, "is_published": 1},
        ["name", "title", "image", "medium", "year", "description", "for_sale", "price"],
        as_dict=True,
    )
    if not art:
        frappe.throw("Artwork not found", frappe.DoesNotExistError)

    if art.price:
        art.price_display = "{:,.0f}".format(art.price)

    context.art = art
    context.title = art.title
