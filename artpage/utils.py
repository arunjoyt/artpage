import frappe


def get_currency_symbol():
    """Symbol for the site's configured currency (System Settings > Currency)."""
    currency = frappe.db.get_single_value("System Settings", "currency") or "EUR"
    return frappe.db.get_value("Currency", currency, "symbol") or currency
