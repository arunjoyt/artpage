"""
Integration tests for the Artist role: DocType permissions and portal page guards.
"""
import types

import frappe
from frappe.tests.utils import FrappeTestCase as IntegrationTestCase


def make_artwork(**kwargs):
    defaults = {
        "doctype": "Artwork",
        "title": "Artist Role Test Art",
        "image": "/files/artist_role_test.jpg",
        "medium": "Oil",
        "is_published": 1,
    }
    defaults.update(kwargs)
    doc = frappe.get_doc(defaults)
    doc.insert(ignore_permissions=True)
    return doc


def make_user(email, roles=None):
    if frappe.db.exists("User", email):
        user = frappe.get_doc("User", email)
    else:
        user = frappe.get_doc({
            "doctype": "User",
            "email": email,
            "first_name": email.split("@")[0],
            "send_welcome_email": 0,
        })
        user.insert(ignore_permissions=True)
    if roles:
        user.add_roles(*roles)
    return user


class TestArtistRoleSetup(IntegrationTestCase):

    def test_artist_role_exists(self):
        self.assertTrue(frappe.db.exists("Role", "Artist"))

    def test_artist_role_has_desk_access_disabled(self):
        self.assertEqual(frappe.db.get_value("Role", "Artist", "desk_access"), 0)

    def test_artist_role_home_page_is_gallery(self):
        self.assertEqual(frappe.db.get_value("Role", "Artist", "home_page"), "/gallery")


class TestArtistRoleDocPermissions(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.artist_user = make_user("artist_role_test@artpage.test", roles=["Artist"]).name
        cls.other_user = make_user("no_role_test@artpage.test").name

    def test_artist_can_create(self):
        frappe.set_user(self.artist_user)
        try:
            doc = frappe.get_doc({
                "doctype": "Artwork",
                "title": "Artist Create Test",
                "image": "/files/test.jpg",
            })
            doc.insert()
            self.assertTrue(frappe.db.exists("Artwork", doc.name))
        finally:
            frappe.set_user("Administrator")

    def test_artist_can_update(self):
        art = make_artwork(title="Artist Update Before")
        frappe.set_user(self.artist_user)
        try:
            doc = frappe.get_doc("Artwork", art.name)
            doc.title = "Artist Update After"
            doc.save()
            self.assertEqual(frappe.db.get_value("Artwork", art.name, "title"), "Artist Update After")
        finally:
            frappe.set_user("Administrator")

    def test_artist_can_delete(self):
        art = make_artwork()
        frappe.set_user(self.artist_user)
        try:
            frappe.delete_doc("Artwork", art.name)
            self.assertFalse(frappe.db.exists("Artwork", art.name))
        finally:
            frappe.set_user("Administrator")

    def test_logged_in_user_without_artist_role_cannot_create(self):
        frappe.set_user(self.other_user)
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

    def test_logged_in_user_without_artist_role_cannot_update(self):
        art = make_artwork()
        frappe.set_user(self.other_user)
        try:
            doc = frappe.get_doc("Artwork", art.name)
            doc.title = "Unauthorized Update"
            with self.assertRaises(frappe.PermissionError):
                doc.save()
        finally:
            frappe.set_user("Administrator")

    def test_logged_in_user_without_artist_role_cannot_delete(self):
        art = make_artwork()
        frappe.set_user(self.other_user)
        try:
            with self.assertRaises(frappe.PermissionError):
                frappe.delete_doc("Artwork", art.name)
        finally:
            frappe.set_user("Administrator")


class TestArtistRolePageGuards(IntegrationTestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.artist_user = make_user("artist_role_page_test@artpage.test", roles=["Artist"]).name
        cls.other_user = make_user("no_role_page_test@artpage.test").name

    def test_manage_allows_artist(self):
        frappe.set_user(self.artist_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.manage import get_context
            get_context(ctx)  # should not raise
        finally:
            frappe.set_user("Administrator")

    def test_manage_blocks_logged_in_user_without_artist_role(self):
        frappe.set_user(self.other_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.manage import get_context
            with self.assertRaises(frappe.PermissionError):
                get_context(ctx)
        finally:
            frappe.set_user("Administrator")

    def test_upload_allows_artist(self):
        frappe.set_user(self.artist_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.upload import get_context
            get_context(ctx)  # should not raise
        finally:
            frappe.set_user("Administrator")

    def test_upload_blocks_logged_in_user_without_artist_role(self):
        frappe.set_user(self.other_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.upload import get_context
            with self.assertRaises(frappe.PermissionError):
                get_context(ctx)
        finally:
            frappe.set_user("Administrator")

    def test_edit_artwork_allows_artist(self):
        art = make_artwork()
        frappe.set_user(self.artist_user)
        try:
            frappe.form_dict["name"] = art.name
            ctx = types.SimpleNamespace()
            from artpage.www.edit_artwork import get_context
            get_context(ctx)
            self.assertEqual(ctx.art.name, art.name)
        finally:
            frappe.form_dict.pop("name", None)
            frappe.set_user("Administrator")

    def test_edit_artwork_blocks_logged_in_user_without_artist_role(self):
        art = make_artwork()
        frappe.set_user(self.other_user)
        try:
            frappe.form_dict["name"] = art.name
            ctx = types.SimpleNamespace()
            from artpage.www.edit_artwork import get_context
            with self.assertRaises(frappe.PermissionError):
                get_context(ctx)
        finally:
            frappe.form_dict.pop("name", None)
            frappe.set_user("Administrator")

    def test_gallery_is_artist_true_for_artist_role_user(self):
        frappe.set_user(self.artist_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.gallery import get_context
            get_context(ctx)
            self.assertTrue(ctx.is_artist)
        finally:
            frappe.set_user("Administrator")

    def test_home_page_is_gallery_for_artist_role_user(self):
        from frappe.website.utils import get_home_page
        original_dev_server = frappe.local.dev_server
        frappe.set_user(self.artist_user)
        try:
            frappe.local.dev_server = 1  # bypass the cached homepage so the role change takes effect
            self.assertEqual(get_home_page(), "gallery")
        finally:
            frappe.local.dev_server = original_dev_server
            frappe.set_user("Administrator")

    def test_gallery_is_artist_false_for_logged_in_user_without_artist_role(self):
        frappe.set_user(self.other_user)
        try:
            ctx = types.SimpleNamespace()
            from artpage.www.gallery import get_context
            get_context(ctx)
            self.assertFalse(ctx.is_artist)
        finally:
            frappe.set_user("Administrator")
