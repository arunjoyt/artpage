import frappe

from artpage.utils import get_currency_symbol, with_cache_buster


def get_context(context):
    context.no_cache = 1
    name = frappe.form_dict.get("name")
    if not name:
        frappe.throw("Artwork not found", frappe.DoesNotExistError)

    art = frappe.db.get_value(
        "Artwork",
        {"name": name, "is_published": 1},
        ["name", "title", "image", "medium", "year", "description", "for_sale", "price", "modified"],
        as_dict=True,
    )
    if not art:
        frappe.throw("Artwork not found", frappe.DoesNotExistError)

    art.image = with_cache_buster(art.image, art.modified)
    if art.price:
        art.price_display = "{}{:,.0f}".format(get_currency_symbol(), art.price)

    context.art = art
    context.title = art.title
