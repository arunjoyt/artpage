"""
Integration tests for portal page get_context functions.
Tests that the Python controllers return correct context data.
"""
import types

import frappe
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase


def make_artwork(**kwargs):
    defaults = {
        "doctype": "Artwork",
        "title": "Portal Test Art",
        "image": "/files/test.jpg",
        "medium": "Watercolour",
        "year": 2023,
        "for_sale": 0,
        "is_published": 1,
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


class TestGalleryContext(IntegrationTestCase):

    def _get_gallery_context(self):
        ctx = types.SimpleNamespace()
        from artpage.www.gallery import get_context
        get_context(ctx)
        return ctx

    def test_published_artworks_appear_in_gallery(self):
        art = make_artwork(is_published=1)
        ctx = self._get_gallery_context()
        names = [a.name for a in ctx.artworks]
        self.assertIn(art.name, names)

    def test_unpublished_artworks_excluded_from_gallery(self):
        art = make_artwork(is_published=0)
        ctx = self._get_gallery_context()
        names = [a.name for a in ctx.artworks]
        self.assertNotIn(art.name, names)

    def test_mediums_list_built_from_artworks(self):
        make_artwork(medium="Sketch", is_published=1)
        make_artwork(medium="Craft", is_published=1)
        ctx = self._get_gallery_context()
        self.assertIn("Sketch", ctx.mediums)
        self.assertIn("Craft", ctx.mediums)

    def test_mediums_excludes_empty_medium(self):
        make_artwork(medium=None, is_published=1)
        ctx = self._get_gallery_context()
        self.assertNotIn(None, ctx.mediums)
        self.assertNotIn("", ctx.mediums)

    def test_mediums_are_unique(self):
        make_artwork(medium="Oil", is_published=1)
        make_artwork(medium="Oil", is_published=1)
        ctx = self._get_gallery_context()
        self.assertEqual(ctx.mediums.count("Oil"), 1)

    def test_price_display_formatted(self):
        make_artwork(for_sale=1, price=12500.0, is_published=1)
        ctx = self._get_gallery_context()
        for_sale_arts = [a for a in ctx.artworks if a.for_sale and a.price]
        self.assertTrue(len(for_sale_arts) > 0)
        self.assertEqual(for_sale_arts[0].price_display, "12,500")

    def test_artworks_ordered_newest_first(self):
        art1 = make_artwork(title="Older")
        art2 = make_artwork(title="Newer")
        ctx = self._get_gallery_context()
        names = [a.name for a in ctx.artworks]
        self.assertLess(names.index(art2.name), names.index(art1.name))

    def test_is_artist_false_for_guest(self):
        frappe.set_user("Guest")
        try:
            ctx = self._get_gallery_context()
            self.assertFalse(ctx.is_artist)
        finally:
            frappe.set_user("Administrator")

    def test_is_artist_true_for_logged_in_user(self):
        ctx = self._get_gallery_context()
        self.assertTrue(ctx.is_artist)


class TestArtworkDetailContext(IntegrationTestCase):

    def _get_artwork_context(self, name):
        ctx = types.SimpleNamespace()
        frappe.form_dict["name"] = name
        from artpage.www.artwork import get_context
        get_context(ctx)
        return ctx

    def test_published_artwork_loads(self):
        art = make_artwork(title="Detail Page Art", is_published=1)
        ctx = self._get_artwork_context(art.name)
        self.assertEqual(ctx.art.name, art.name)
        self.assertEqual(ctx.art.title, "Detail Page Art")

    def test_unpublished_artwork_raises_404(self):
        art = make_artwork(is_published=0)
        self.assertRaises(frappe.DoesNotExistError, self._get_artwork_context, art.name)

    def test_nonexistent_artwork_raises_404(self):
        self.assertRaises(frappe.DoesNotExistError, self._get_artwork_context, "ART-DOES-NOT-EXIST")

    def test_no_name_param_raises_error(self):
        frappe.form_dict.pop("name", None)
        ctx = types.SimpleNamespace()
        from artpage.www.artwork import get_context
        self.assertRaises(frappe.DoesNotExistError, get_context, ctx)

    def test_price_display_on_for_sale_artwork(self):
        art = make_artwork(for_sale=1, price=3000.0, is_published=1)
        ctx = self._get_artwork_context(art.name)
        self.assertEqual(ctx.art.price_display, "3,000")

    def test_page_title_set_to_artwork_title(self):
        art = make_artwork(title="My Landscape", is_published=1)
        ctx = self._get_artwork_context(art.name)
        self.assertEqual(ctx.title, "My Landscape")


class TestManageContext(IntegrationTestCase):

    def test_manage_shows_all_artworks(self):
        pub   = make_artwork(title="Published",   is_published=1)
        draft = make_artwork(title="Draft",       is_published=0)

        ctx = types.SimpleNamespace()
        from artpage.www.manage import get_context
        get_context(ctx)

        names = [a.name for a in ctx.artworks]
        self.assertIn(pub.name,   names)
        self.assertIn(draft.name, names)

    def test_manage_redirects_guest(self):
        frappe.set_user("Guest")
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.manage import get_context
            self.assertRaises(frappe.Redirect, get_context, ctx)
        finally:
            frappe.set_user("Administrator")
