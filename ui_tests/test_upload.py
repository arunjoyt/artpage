"""
UI tests for the upload and manage pages.
"""
import os
import re
import tempfile

from playwright.sync_api import expect

from conftest import api_create, api_delete

BASE_URL = "http://artpage.localhost:8005"
SCREENSHOTS = "ui_tests/screenshots"


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
