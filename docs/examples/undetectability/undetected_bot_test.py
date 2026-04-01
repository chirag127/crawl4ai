"""
Bot Detection Test - Compare Regular vs Undetected
Tests browser fingerprinting differences at bot.sannysoft.com
"""

import asyncio

from crawl4ai import (AsyncWebCrawler, BrowserConfig, CrawlerRunConfig,
                      CrawlResult, UndetectedAdapter)
from crawl4ai.async_crawler_strategy import AsyncPlaywrightCrawlerStrategy

# Bot detection test site
TEST_URL = "https://bot.sannysoft.com"


def analyze_bot_detection(result: CrawlResult) -> dict:
    """Analyze bot detection results from the page"""
    detections = {
        "webdriver": False,
        "headless": False,
        "automation": False,
        "user_agent": False,
        "total_tests": 0,
        "failed_tests": 0,
    }

    if not result.success or not result.html:
        return detections

    # Look for specific test results in the HTML
    html_lower = result.html.lower()

    # Check for common bot indicators
    if "webdriver" in html_lower and ("fail" in html_lower or "true" in html_lower):
        detections["webdriver"] = True
        detections["failed_tests"] += 1

    if "headless" in html_lower and ("fail" in html_lower or "true" in html_lower):
        detections["headless"] = True
        detections["failed_tests"] += 1

    if "automation" in html_lower and "detected" in html_lower:
        detections["automation"] = True
        detections["failed_tests"] += 1

    # Count total tests (approximate)
    detections["total_tests"] = html_lower.count("test") + html_lower.count("check")

    return detections


async def test_browser_mode(adapter_name: str, adapter=None):
    """Test a browser mode and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {adapter_name}")
    print(f"{'='*60}")

    browser_config = BrowserConfig(
        headless=False,  # Run in headed mode for better results
        verbose=True,
        viewport_width=1920,
        viewport_height=1080,
    )

    if adapter:
        # Use undetected mode
        crawler_strategy = AsyncPlaywrightCrawlerStrategy(
            browser_config=browser_config, browser_adapter=adapter
        )
        crawler = AsyncWebCrawler(
            crawler_strategy=crawler_strategy, config=browser_config
        )
    else:
        # Use regular mode
        crawler = AsyncWebCrawler(config=browser_config)

    async with crawler:
        config = CrawlerRunConfig(
            delay_before_return_html=3.0,  # Let detection scripts run
            wait_for_images=True,
            screenshot=True,
            simulate_user=False,  # Don't simulate for accurate detection
        )

        result = await crawler.arun(url=TEST_URL, config=config)

        print(f"\n✓ Success: {result.success}")
        print(f"✓ Status Code: {result.status_code}")

        if result.success:
            # Analyze detection results
            detections = analyze_bot_detection(result)

            print("\n🔍 Bot Detection Analysis:")
            print(
                f"  - WebDriver Detected: {'❌ Yes' if detections['webdriver'] else '✅ No'}"
            )
            print(
                f"  - Headless Detected: {'❌ Yes' if detections['headless'] else '✅ No'}"
            )
            print(
                f"  - Automation Detected: {'❌ Yes' if detections['automation'] else '✅ No'}"
            )
            print(f"  - Failed Tests: {detections['failed_tests']}")

            # Show some content
            if result.markdown.raw_markdown:
                print("\nContent preview:")
                lines = result.markdown.raw_markdown.split("\n")
                for line in lines[:20]:  # Show first 20 lines
                    if any(
                        keyword in line.lower()
                        for keyword in ["test", "pass", "fail", "yes", "no"]
                    ):
                        print(f"  {line.strip()}")

        return result, detections if result.success else {}


async def main():
    """Run the comparison"""
    print("🤖 Crawl4AI - Bot Detection Test")
    print(f"Testing at: {TEST_URL}")
    print("This site runs various browser fingerprinting tests\n")

    # Test regular browser
    regular_result, regular_detections = await test_browser_mode("Regular Browser")

    # Small delay
    await asyncio.sleep(2)

    # Test undetected browser
    undetected_adapter = UndetectedAdapter()
    undetected_result, undetected_detections = await test_browser_mode(
        "Undetected Browser", undetected_adapter
    )

    # Summary comparison
    print(f"\n{'='*60}")
    print("COMPARISON SUMMARY")
    print(f"{'='*60}")

    print(f"\n{'Test':<25} {'Regular':<15} {'Undetected':<15}")
    print(f"{'-'*55}")

    if regular_detections and undetected_detections:
        print(
            f"{'WebDriver Detection':<25} {'❌ Detected' if regular_detections['webdriver'] else '✅ Passed':<15} {'❌ Detected' if undetected_detections['webdriver'] else '✅ Passed':<15}"
        )
        print(
            f"{'Headless Detection':<25} {'❌ Detected' if regular_detections['headless'] else '✅ Passed':<15} {'❌ Detected' if undetected_detections['headless'] else '✅ Passed':<15}"
        )
        print(
            f"{'Automation Detection':<25} {'❌ Detected' if regular_detections['automation'] else '✅ Passed':<15} {'❌ Detected' if undetected_detections['automation'] else '✅ Passed':<15}"
        )
        print(
            f"{'Failed Tests':<25} {regular_detections['failed_tests']:<15} {undetected_detections['failed_tests']:<15}"
        )

    print(f"\n{'='*60}")

    if undetected_detections.get("failed_tests", 0) < regular_detections.get(
        "failed_tests", 1
    ):
        print("✅ Undetected browser performed better at evading detection!")
    else:
        print("ℹ️  Both browsers had similar detection results")


if __name__ == "__main__":
    asyncio.run(main())
