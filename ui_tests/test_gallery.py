"""
UI tests for the public gallery page.
"""
import pytest
from playwright.sync_api import expect

from conftest import api_create, api_delete

BASE_URL = "http://artpage.localhost:8005"
SCREENSHOTS = "ui_tests/screenshots"


def test_gallery_page_loads(guest_page):
    guest_page.goto(f"{BASE_URL}/gallery")
    expect(guest_page).to_have_title("Gallery")
    guest_page.screenshot(path=f"{SCREENSHOTS}/gallery_empty_or_populated.png", full_page=True)


def test_gallery_heading_visible(guest_page):
    guest_page.goto(f"{BASE_URL}/gallery")
    heading = guest_page.locator("h1", has_text="Gallery")
    expect(heading).to_be_visible()


def test_gallery_shows_published_artworks(logged_in_page):
    artwork_name = api_create(logged_in_page, title="UI Test Artwork", medium="Digital")

    try:
        logged_in_page.goto(f"{BASE_URL}/gallery")
        card = logged_in_page.locator(f'.ap-card[data-medium="Digital"]').first
        expect(card).to_be_visible()
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/gallery_with_artwork.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_gallery_filter_tabs_appear_when_mediums_exist(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Filter Test Art", medium="Watercolour")

    try:
        logged_in_page.goto(f"{BASE_URL}/gallery")
        filter_btn = logged_in_page.locator(".ap-filter-btn", has_text="Watercolour")
        expect(filter_btn).to_be_visible()
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/gallery_filter_tabs.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)


def test_gallery_filter_hides_non_matching_cards(logged_in_page):
    n1 = api_create(logged_in_page, title="Oil Art", medium="Oil")
    n2 = api_create(logged_in_page, title="Sketch Art", medium="Sketch")

    try:
        logged_in_page.goto(f"{BASE_URL}/gallery")
        logged_in_page.locator(".ap-filter-btn", has_text="Oil").click()
        expect(logged_in_page.locator(f'.ap-card[data-medium="Sketch"]').first).to_be_hidden()
        expect(logged_in_page.locator(f'.ap-card[data-medium="Oil"]').first).to_be_visible()
    finally:
        api_delete(logged_in_page, n1)
        api_delete(logged_in_page, n2)


def test_gallery_card_links_to_detail(logged_in_page):
    artwork_name = api_create(logged_in_page, title="Clickable Art", medium="Craft")

    try:
        logged_in_page.goto(f"{BASE_URL}/gallery")
        card = logged_in_page.locator(f'a.ap-card[href*="{artwork_name}"]').first
        expect(card).to_be_visible()
        card.click()
        expect(logged_in_page).to_have_url(f"{BASE_URL}/artwork?name={artwork_name}")
    finally:
        api_delete(logged_in_page, artwork_name)


def test_for_sale_badge_visible(logged_in_page):
    artwork_name = api_create(logged_in_page, title="For Sale Art", for_sale=1, price=3000)

    try:
        logged_in_page.goto(f"{BASE_URL}/gallery")
        badge = logged_in_page.locator(f'a.ap-card[href*="{artwork_name}"] .ap-sale-badge')
        expect(badge).to_be_visible()
        logged_in_page.screenshot(path=f"{SCREENSHOTS}/gallery_for_sale_badge.png", full_page=True)
    finally:
        api_delete(logged_in_page, artwork_name)
