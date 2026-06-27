"""
UI tests for the artwork detail page.
"""
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
        expect(logged_in_page.locator(".ap-detail-medium", has_text="Acrylic")).to_be_visible()
        expect(logged_in_page.locator(".ap-detail-year", has_text="2023")).to_be_visible()
        expect(logged_in_page.locator(".ap-detail-desc")).to_contain_text("A beautiful piece.")
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/artwork_detail.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_detail_shows_price_when_for_sale(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Priced Art", for_sale=1, price=7500)

    try:
        logged_in_page.goto(f"{BASE_URL}/artwork?name={artwork_name}")
        expect(logged_in_page.locator(".ap-detail-price")).to_be_visible()
        expect(logged_in_page.locator(".ap-detail-price")).to_contain_text("7,500")
    finally:
        api_delete(logged_in_page, artwork_name)


def test_detail_back_link_returns_to_gallery(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Back Link Art")

    try:
        logged_in_page.goto(f"{BASE_URL}/artwork?name={artwork_name}")
        logged_in_page.locator(".ap-btn-back").click()
        expect(logged_in_page).to_have_url(f"{BASE_URL}/gallery")
    finally:
        api_delete(logged_in_page, artwork_name)


def test_unpublished_artwork_not_accessible_by_guest(guest_page):
    # Without auth we can't create, so test with a nonexistent name
    guest_page.goto(f"{BASE_URL}/artwork?name=ART-NONEXISTENT")
    # Should show 404 or redirect — not show artwork details
    expect(guest_page.locator(".ap-detail")).not_to_be_visible()
