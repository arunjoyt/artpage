import frappe
from frappe.tests.utils import FrappeTestCase


def make_artwork(**kwargs):
    defaults = {
        "doctype": "Artwork",
        "title": "Test Painting",
        "image": "/files/test.jpg",
        "medium": "Oil on canvas",
        "year": 2024,
        "description": "A test artwork",
        "for_sale": 0,
        "is_published": 1,
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


class TestArtwork(FrappeTestCase):

    def test_artwork_creation(self):
        art = make_artwork()
        self.assertTrue(art.name.startswith("ART-"))
        self.assertEqual(art.title, "Test Painting")
        self.assertEqual(art.medium, "Oil on canvas")

    def test_is_published_defaults_to_1(self):
        art = make_artwork()
        self.assertEqual(art.is_published, 1)

    def test_for_sale_defaults_to_0(self):
        art = make_artwork()
        self.assertEqual(art.for_sale, 0)

    def test_autoname_has_art_prefix(self):
        art = make_artwork(title="Prefix Test")
        self.assertTrue(art.name.startswith("ART-"))

    def test_autoname_is_sequential(self):
        art1 = make_artwork(title="Sequential 1")
        art2 = make_artwork(title="Sequential 2")
        self.assertNotEqual(art1.name, art2.name)

    def test_unpublished_artwork_saves(self):
        art = make_artwork(is_published=0)
        self.assertEqual(art.is_published, 0)

    def test_for_sale_with_price(self):
        art = make_artwork(for_sale=1, price=5000)
        self.assertEqual(art.for_sale, 1)
        self.assertEqual(art.price, 5000)

    def test_update_title(self):
        art = make_artwork(title="Original Title")
        art.title = "Updated Title"
        art.save()
        reloaded = frappe.get_doc("Artwork", art.name)
        self.assertEqual(reloaded.title, "Updated Title")

    def test_update_published_status(self):
        art = make_artwork(is_published=1)
        art.is_published = 0
        art.save()
        reloaded = frappe.get_doc("Artwork", art.name)
        self.assertEqual(reloaded.is_published, 0)

    def test_delete_artwork(self):
        art = make_artwork()
        name = art.name
        frappe.delete_doc("Artwork", name, ignore_permissions=True)
        self.assertFalse(frappe.db.exists("Artwork", name))

    def test_year_field_accepts_integer(self):
        art = make_artwork(year=1998)
        self.assertEqual(art.year, 1998)

    def test_description_field(self):
        art = make_artwork(description="A beautiful sunset painting")
        self.assertEqual(art.description, "A beautiful sunset painting")

    def test_guest_cannot_create(self):
        frappe.set_user("Guest")
        try:
            doc = frappe.get_doc({
                "doctype": "Artwork",
                "title": "Guest Creation Attempt",
                "image": "/files/test.jpg",
            })
            self.assertRaises(frappe.PermissionError, doc.insert)
        finally:
            frappe.set_user("Administrator")

    def test_guest_can_read_published(self):
        art = make_artwork(is_published=1, title="Public Artwork")
        frappe.set_user("Guest")
        try:
            result = frappe.db.get_value("Artwork", art.name, "title")
            self.assertEqual(result, "Public Artwork")
        finally:
            frappe.set_user("Administrator")
