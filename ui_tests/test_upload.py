"""
UI tests for the upload and manage pages.
"""
import base64
import os
import re
import tempfile

from playwright.sync_api import expect

from conftest import api_create, api_delete

BASE_URL = "http://artpage.localhost:8005"
SCREENSHOTS = "ui_tests/screenshots"

# 1x1 transparent PNG
TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="
)


def _find_artwork_by_title(page, title):
    return page.evaluate(
        """async (title) => {
            const r = await fetch('/api/method/frappe.client.get_list?doctype=Artwork&filters='
                + encodeURIComponent(JSON.stringify([["title", "=", title]])),
                { headers: {'X-Frappe-CSRF-Token': frappe.csrf_token} });
            const data = await r.json();
            return data.message.length ? data.message[0].name : null;
        }""",
        title,
    )


def _get_artwork_field(page, name, fieldname):
    return page.evaluate(
        """async ([name, fieldname]) => {
            const r = await fetch('/api/method/frappe.client.get_value?doctype=Artwork'
                + '&filters=' + encodeURIComponent(JSON.stringify({name}))
                + '&fieldname=' + encodeURIComponent(fieldname),
                { headers: {'X-Frappe-CSRF-Token': frappe.csrf_token} });
            const data = await r.json();
            return data.message ? data.message[fieldname] : null;
        }""",
        [name, fieldname],
    )


def test_upload_page_redirects_guest_to_login(guest_page):
    guest_page.goto(f"{BASE_URL}/upload")
    expect(guest_page).to_have_url(re.compile(r".*/login\?redirect-to=/upload"))
    guest_page.screenshot(path=f"{SCREENSHOTS}/upload_guest_redirect.png", full_page=True)


def test_manage_page_redirects_guest_to_login(guest_page):
    guest_page.goto(f"{BASE_URL}/manage")
    expect(guest_page).to_have_url(re.compile(r".*/login\?redirect-to=/manage"))


def test_upload_page_accessible_when_logged_in(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/upload")
    expect(logged_in_page.locator("h1", has_text="Upload Artwork")).to_be_visible()
    logged_in_page.screenshot(path=f"{SCREENSHOTS}/upload_form.png", full_page=True)


def test_upload_form_has_required_fields(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/upload")
    expect(logged_in_page.locator("#f-title")).to_be_visible()
    expect(logged_in_page.locator("#f-medium")).to_be_visible()
    expect(logged_in_page.locator("#f-year")).to_be_visible()
    expect(logged_in_page.locator("#f-desc")).to_be_visible()
    expect(logged_in_page.locator("#f-forsale")).to_be_visible()
    expect(logged_in_page.locator("#btn-submit")).to_be_visible()


def test_price_field_hidden_until_for_sale_checked(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/upload")
    price_group = logged_in_page.locator("#price-group")
    expect(price_group).to_contain_class("hidden")

    logged_in_page.locator("#f-forsale").check()
    expect(price_group).not_to_contain_class("hidden")
    logged_in_page.screenshot(path=f"{SCREENSHOTS}/upload_price_visible.png", full_page=True)


def test_upload_submit_without_image_shows_error(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/upload")
    logged_in_page.fill("#f-title", "No Image Art")
    logged_in_page.click("#btn-submit")
    status = logged_in_page.locator("#status-msg")
    expect(status).to_contain_class("bg-red-50")
    expect(status).to_contain_text("photo")


def test_upload_submit_without_title_shows_error(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/upload")
    # Don't fill title, don't attach file
    logged_in_page.click("#btn-submit")
    status = logged_in_page.locator("#status-msg")
    expect(status).to_contain_class("bg-red-50")


def test_upload_submit_with_image_succeeds(logged_in_page):
    """Regression test: upload_file must not send a doctype without a docname
    (Frappe's File.validate_attachment_references rejects that combination)."""
    tmp_path = None
    artwork_name = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(TINY_PNG)
            tmp_path = f.name

        logged_in_page.goto(f"{BASE_URL}/upload")
        logged_in_page.fill("#f-title", "Real Upload Test")
        logged_in_page.set_input_files("#img-input", tmp_path)
        logged_in_page.click("#btn-submit")
        logged_in_page.wait_for_url(re.compile(r".*/gallery"))
        expect(logged_in_page).to_have_url(re.compile(r".*/gallery"))

        artwork_name = _find_artwork_by_title(logged_in_page, "Real Upload Test")
        assert artwork_name, "Artwork was not created after upload"
    finally:
        if tmp_path:
            os.remove(tmp_path)
        if artwork_name:
            api_delete(logged_in_page, artwork_name)


def test_manage_page_shows_artworks(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Manage List Art")

    try:
        logged_in_page.goto(f"{BASE_URL}/manage")
        expect(logged_in_page.locator(f'a[href="/edit-artwork?name={artwork_name}"]')).to_be_visible()
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/manage_list.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_manage_upload_button_links_to_upload(logged_in_page):
    logged_in_page.goto(f"{BASE_URL}/manage")
    upload_btn = logged_in_page.locator('a[href="/upload"]').first
    expect(upload_btn).to_be_visible()


def test_edit_artwork_page_prepopulates_fields(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Edit Prepop Test", medium="Pastel", year=2022)

    try:
        logged_in_page.goto(f"{BASE_URL}/edit-artwork?name={artwork_name}")
        expect(logged_in_page.locator("#f-title")).to_have_value("Edit Prepop Test")
        expect(logged_in_page.locator("#f-medium")).to_have_value("Pastel")
        expect(logged_in_page.locator("#f-year")).to_have_value("2022")
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/edit_artwork_form.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_edit_artwork_save_persists_changes(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Edit Save Before", medium="Oil")

    try:
        logged_in_page.goto(f"{BASE_URL}/edit-artwork?name={artwork_name}")
        logged_in_page.fill("#f-title", "Edit Save After")
        logged_in_page.fill("#f-medium", "Watercolour")
        logged_in_page.click("#btn-save")
        logged_in_page.wait_for_url(re.compile(r".*/manage"))
        expect(logged_in_page).to_have_url(re.compile(r".*/manage"))

        assert _get_artwork_field(logged_in_page, artwork_name, "title") == "Edit Save After"
        assert _get_artwork_field(logged_in_page, artwork_name, "medium") == "Watercolour"
    finally:
        api_delete(logged_in_page, artwork_name)


def test_edit_artwork_save_with_new_image_succeeds(logged_in_page):
    """Regression test: the edit form's upload_file call must not send a
    doctype without a docname either (same bug as the upload page)."""
    artwork_name = api_create(logged_in_page, title="Edit Image Swap")
    tmp_path = None

    try:
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            f.write(TINY_PNG)
            tmp_path = f.name

        logged_in_page.goto(f"{BASE_URL}/edit-artwork?name={artwork_name}")
        original_image = _get_artwork_field(logged_in_page, artwork_name, "image")
        logged_in_page.set_input_files("#img-input", tmp_path)
        logged_in_page.click("#btn-save")
        logged_in_page.wait_for_url(re.compile(r".*/manage"))
        expect(logged_in_page).to_have_url(re.compile(r".*/manage"))

        new_image = _get_artwork_field(logged_in_page, artwork_name, "image")
        assert new_image and new_image != original_image
    finally:
        if tmp_path:
            os.remove(tmp_path)
        api_delete(logged_in_page, artwork_name)


def test_edit_artwork_delete_removes_artwork(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Delete Me Test")

    logged_in_page.goto(f"{BASE_URL}/edit-artwork?name={artwork_name}")
    logged_in_page.once("dialog", lambda dialog: dialog.accept())
    logged_in_page.click("#btn-delete")
    logged_in_page.wait_for_url(re.compile(r".*/manage"))
    expect(logged_in_page).to_have_url(re.compile(r".*/manage"))

    assert _find_artwork_by_title(logged_in_page, "Delete Me Test") is None


def test_edit_artwork_publish_toggle_persists(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Toggle Publish Test", is_published=1)

    try:
        logged_in_page.goto(f"{BASE_URL}/edit-artwork?name={artwork_name}")
        published_checkbox = logged_in_page.locator("#f-published")
        expect(published_checkbox).to_be_checked()

        published_checkbox.uncheck()
        logged_in_page.click("#btn-save")
        logged_in_page.wait_for_url(re.compile(r".*/manage"))

        assert _get_artwork_field(logged_in_page, artwork_name, "is_published") == 0
    finally:
        api_delete(logged_in_page, artwork_name)
