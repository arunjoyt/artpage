"""
Playwright configuration for Artpage UI tests.

Prerequisites:
  1. bench start (server must be running)
  2. artpage.localhost must resolve: add to /etc/hosts if needed
       127.0.0.1  artpage.localhost
  3. Install browsers once:
       /path/to/bench/env/bin/playwright install chromium

Run:
  cd apps/artpage
  /path/to/bench/env/bin/pytest ui_tests/ -v --base-url http://artpage.localhost:8005
"""
import pytest


BASE_URL = "http://artpage.localhost:8005"
ADMIN_USER = "Administrator"
ADMIN_PASS = "admin"


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    return {**browser_context_args, "viewport": {"width": 390, "height": 844}}  # iPhone 14


@pytest.fixture
def logged_in_page(page):
    """Returns a Playwright page already authenticated as Administrator."""
    page.goto(f"{BASE_URL}/login")
    page.fill("#login_email", ADMIN_USER)
    page.fill("#login_password", ADMIN_PASS)
    page.click("button.btn-login")
    # wait_for_url with /** matches the login page itself; wait for navigation away instead
    page.wait_for_function("() => !window.location.pathname.startsWith('/login')")
    return page


@pytest.fixture
def guest_page(page):
    """Returns a Playwright page with no session (guest)."""
    return page


def _frappe_ready(page):
    """Navigate to gallery and wait for all scripts to load (frappe is available after networkidle)."""
    page.goto(f"{BASE_URL}/gallery", wait_until="networkidle")


def api_create(page, **kwargs):
    """Create a test Artwork via fetch (browser session, auto CSRF). Returns the new doc name."""
    _frappe_ready(page)
    doc = {
        "doctype": "Artwork",
        "image": "/assets/frappe/images/frappe-framework-logo.svg",
        "is_published": 1,
        **kwargs,
    }
    name = page.evaluate(
        """async (doc) => {
            const r = await fetch('/api/method/frappe.client.insert', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Frappe-CSRF-Token': frappe.csrf_token,
                },
                body: JSON.stringify({doc}),
            });
            if (!r.ok) throw new Error('Insert failed ' + r.status + ': ' + await r.text());
            const data = await r.json();
            return data.message.name;
        }""",
        doc,
    )
    return name


def api_delete(page, name):
    """Delete a test Artwork via fetch (browser session, auto CSRF)."""
    _frappe_ready(page)
    page.evaluate(
        """async ([dt, n]) => {
            await fetch('/api/v2/document/' + dt + '/' + n, {
                method: 'DELETE',
                headers: {'X-Frappe-CSRF-Token': frappe.csrf_token},
            });
        }""",
        ["Artwork", name],
    )
