import frappe


def get_currency_symbol():
    """Symbol for the site's configured currency (System Settings > Currency)."""
    currency = frappe.db.get_single_value("System Settings", "currency") or "EUR"
    return frappe.db.get_value("Currency", currency, "symbol") or currency


def with_cache_buster(url, modified):
    """Append ?v=<timestamp> so an edited image (e.g. rotated in place) isn't
    served stale from the browser's cache for its unchanged URL."""
    if not url or not modified:
        return url
    return f"{url}?v={int(frappe.utils.get_datetime(modified).timestamp())}"
