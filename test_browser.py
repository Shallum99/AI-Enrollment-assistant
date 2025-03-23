from playwright.sync_api import sync_playwright
import time

def test_browser():
    """Simple test to check if browser automation is working"""
    print("Testing browser automation...")
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        
        # Navigate to a test site
        print("Navigating to example.com...")
        page.goto("https://example.com")
        
        # Get the title
        title = page.title()
        print(f"Page title: {title}")
        
        # Take a screenshot
        page.screenshot(path="browser_test.png")
        print("Screenshot saved as browser_test.png")
        
        # Wait a moment to see the page
        time.sleep(3)
        
        browser.close()
        return True

if __name__ == "__main__":
    test_browser()