import frappe

from artpage.utils import get_currency_symbol, with_cache_buster


def get_context(context):
    context.no_cache = 1
    artworks = frappe.db.get_all(
        "Artwork",
        filters={"is_published": 1},
        fields=["name", "title", "image", "medium", "for_sale", "price", "modified"],
        order_by="creation desc",
        ignore_permissions=True,
    )
    currency_symbol = get_currency_symbol()
    for art in artworks:
        art.image = with_cache_buster(art.image, art.modified)
        if art.price:
            art.price_display = "{}{:,.0f}".format(currency_symbol, art.price)
    context.artworks = artworks
    mediums = sorted({a.medium for a in artworks if a.medium})
    context.mediums = mediums
    context.is_artist = frappe.session.user != "Guest" and frappe.has_permission("Artwork", "write")

    context.site_title = (
        frappe.db.get_value("Website Settings", "Website Settings", "app_name") or ""
    )
