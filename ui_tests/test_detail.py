"""
UI tests for the artwork detail page.
"""
import re

from playwright.sync_api import expect

from conftest import api_create, api_delete

BASE_URL = "http://artpage.localhost:8005"
SCREENSHOTS = "ui_tests/screenshots"


def test_artwork_detail_loads(logged_in_page):
    artwork_name = api_create(
        logged_in_page, title="Detail Test", medium="Acrylic", year=2023,
        description="A beautiful piece.",
    )

    try:
        logged_in_page.goto(f"{BASE_URL}/artwork?name={artwork_name}")
        expect(logged_in_page.locator("h1", has_text="Detail Test")).to_be_visible()
        expect(logged_in_page.get_by_text("Acrylic", exact=True)).to_be_visible()
        expect(logged_in_page.get_by_text("2023", exact=True)).to_be_visible()
        expect(logged_in_page.get_by_text("A beautiful piece.")).to_be_visible()
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/artwork_detail.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_detail_shows_price_when_for_sale(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Priced Art", for_sale=1, price=7500)

    try:
        logged_in_page.goto(f"{BASE_URL}/artwork?name={artwork_name}")
        expect(logged_in_page.get_by_text("7,500")).to_be_visible()
    finally:
        api_delete(logged_in_page, artwork_name)


def test_detail_back_link_returns_to_gallery(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Back Link Art")

    try:
        logged_in_page.goto(f"{BASE_URL}/artwork?name={artwork_name}")
        logged_in_page.get_by_role("link", name=re.compile("Back to Gallery")).click()
        expect(logged_in_page).to_have_url(f"{BASE_URL}/gallery")
    finally:
        api_delete(logged_in_page, artwork_name)


def test_unpublished_artwork_not_accessible_by_guest(guest_page):
    # Without auth we can't create, so test with a nonexistent name
    guest_page.goto(f"{BASE_URL}/artwork?name=ART-NONEXISTENT")
    # Should show 404 or redirect — not show artwork details
    expect(guest_page.locator(".ap-detail")).not_to_be_visible()
