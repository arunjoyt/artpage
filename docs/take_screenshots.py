"""
Regenerates the curated README screenshots in docs/screenshots/.

Read-only: does not create, modify, or delete any Artwork records. Run this
by hand after a meaningful UI change to /gallery, /upload, /manage, or
/edit-artwork, then review the diffs before committing.

Assumes the dev site already has real demo data seeded (not test fixtures) —
specifically an "Oil on canvas" medium (for the filter-tab screenshot) and an
artwork titled "The Starry Night" (for the detail-page screenshot). Update
those two lookups below if the demo data changes.

Prerequisites:
  1. bench start (server must be running)
  2. artpage.localhost must resolve (see ui_tests/conftest.py)

Run:
  /path/to/bench/env/bin/python docs/take_screenshots.py
"""
from pathlib import Path

from playwright.sync_api import sync_playwright

BASE_URL = "http://artpage.localhost:8005"
OUT = Path(__file__).parent / "screenshots"

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(viewport={"width": 390, "height": 844})
    page = context.new_page()

    page.goto(f"{BASE_URL}/login")
    page.fill("#login_email", "Administrator")
    page.fill("#login_password", "admin")
    page.click("button.btn-login")
    page.wait_for_function("() => !window.location.pathname.startsWith('/login')")

    # Gallery (masonry)
    page.goto(f"{BASE_URL}/gallery", wait_until="networkidle")
    page.screenshot(path=f"{OUT}/gallery_with_artwork.png", full_page=True)

    # Filter active
    page.locator("button", has_text="Oil on canvas").first.click()
    page.wait_for_timeout(300)
    page.screenshot(path=f"{OUT}/gallery_filter_tabs.png", full_page=True)

    # Mobile (same viewport; re-captured fresh for consistency)
    page.goto(f"{BASE_URL}/gallery", wait_until="networkidle")
    page.screenshot(path=f"{OUT}/gallery_mobile.png", full_page=True)

    # Artwork detail
    page.get_by_text("The Starry Night").first.click()
    page.wait_for_load_state("networkidle")
    page.screenshot(path=f"{OUT}/artwork_detail.png", full_page=True)

    # Manage list
    page.goto(f"{BASE_URL}/manage", wait_until="networkidle")
    page.screenshot(path=f"{OUT}/manage_list.png", full_page=True)

    # Upload form (empty)
    page.goto(f"{BASE_URL}/upload", wait_until="networkidle")
    page.screenshot(path=f"{OUT}/upload_form.png", full_page=True)

    browser.close()

print("Done.")
