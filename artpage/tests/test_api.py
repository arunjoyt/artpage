"""
Integration tests for Artwork DocType permissions and API behaviour.
"""
import frappe
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase


def make_artwork(**kwargs):
    defaults = {
        "doctype": "Artwork",
        "title": "API Test Art",
        "image": "/files/api_test.jpg",
        "medium": "Sketch",
        "is_published": 1,
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


class TestArtworkPermissions(IntegrationTestCase):

    def test_system_manager_can_create(self):
        doc = frappe.get_doc({
            "doctype": "Artwork",
            "title": "Permission Create Test",
            "image": "/files/test.jpg",
        })
        doc.insert()  # no ignore_permissions — must pass normally
        self.assertTrue(frappe.db.exists("Artwork", doc.name))

    def test_system_manager_can_update(self):
        art = make_artwork(title="Before Update")
        art.title = "After Update"
        art.save()  # no ignore_permissions
        self.assertEqual(frappe.db.get_value("Artwork", art.name, "title"), "After Update")

    def test_system_manager_can_delete(self):
        art = make_artwork()
        name = art.name
        frappe.delete_doc("Artwork", name)
        self.assertFalse(frappe.db.exists("Artwork", name))

    def test_guest_cannot_create(self):
        frappe.set_user("Guest")
        try:
            doc = frappe.get_doc({
                "doctype": "Artwork",
                "title": "Unauthorized Create",
                "image": "/files/test.jpg",
            })
            with self.assertRaises(frappe.PermissionError):
                doc.insert()
        finally:
            frappe.set_user("Administrator")

    def test_guest_cannot_update(self):
        art = make_artwork()
        frappe.set_user("Guest")
        try:
            guest_doc = frappe.get_doc("Artwork", art.name)
            guest_doc.title = "Guest Update Attempt"
            with self.assertRaises(frappe.PermissionError):
                guest_doc.save()
        finally:
            frappe.set_user("Administrator")

    def test_guest_cannot_delete(self):
        art = make_artwork()
        frappe.set_user("Guest")
        try:
            with self.assertRaises(frappe.PermissionError):
                frappe.delete_doc("Artwork", art.name)
        finally:
            frappe.set_user("Administrator")

    def test_guest_can_read_published(self):
        art = make_artwork(is_published=1, title="Readable Art")
        frappe.set_user("Guest")
        try:
            title = frappe.db.get_value("Artwork", art.name, "title")
            self.assertEqual(title, "Readable Art")
        finally:
            frappe.set_user("Administrator")


class TestArtworkQueries(IntegrationTestCase):

    def test_get_all_published_returns_only_published(self):
        pub   = make_artwork(is_published=1)
        draft = make_artwork(is_published=0)

        results = frappe.db.get_all(
            "Artwork",
            filters={"is_published": 1, "name": ["in", [pub.name, draft.name]]},
            fields=["name"],
            ignore_permissions=True,
        )
        names = [r.name for r in results]
        self.assertIn(pub.name, names)
        self.assertNotIn(draft.name, names)

    def test_for_sale_filter(self):
        for_sale     = make_artwork(for_sale=1, price=2000)
        not_for_sale = make_artwork(for_sale=0)

        results = frappe.db.get_all(
            "Artwork",
            filters={"for_sale": 1, "name": ["in", [for_sale.name, not_for_sale.name]]},
            fields=["name"],
            ignore_permissions=True,
        )
        names = [r.name for r in results]
        self.assertIn(for_sale.name, names)
        self.assertNotIn(not_for_sale.name, names)

    def test_order_by_creation_desc(self):
        art1 = make_artwork(title="First Created")
        art2 = make_artwork(title="Second Created")

        results = frappe.db.get_all(
            "Artwork",
            filters={"name": ["in", [art1.name, art2.name]]},
            fields=["name"],
            order_by="creation desc",
            ignore_permissions=True,
        )
        self.assertEqual(results[0].name, art2.name)
        self.assertEqual(results[1].name, art1.name)
