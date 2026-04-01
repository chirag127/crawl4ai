#!/usr/bin/env python3
"""
🚀 Crawl4AI v0.7.5 - Docker Hooks System Complete Demonstration
================================================================

This file demonstrates the NEW Docker Hooks System introduced in v0.7.5.

The Docker Hooks System is a completely NEW feature that provides pipeline
customization through user-provided Python functions. It offers three approaches:

1. String-based hooks for REST API
2. hooks_to_string() utility to convert functions
3. Docker Client with automatic conversion (most convenient)

All three approaches are part of this NEW v0.7.5 feature!

Perfect for video recording and demonstration purposes.

Requirements:
- Docker container running: docker run -p 11235:11235 unclecode/crawl4ai:latest
- crawl4ai v0.7.5 installed: pip install crawl4ai==0.7.5
"""

import asyncio
import time

import requests

# Import Crawl4AI components
from crawl4ai import hooks_to_string
from crawl4ai.docker_client import Crawl4aiDockerClient

# Configuration
DOCKER_URL = "http://localhost:11235"
# DOCKER_URL = "http://localhost:11234"
TEST_URLS = [
    # "https://httpbin.org/html",
    "https://www.kidocode.com",
    "https://quotes.toscrape.com",
]


def print_section(title: str, description: str = ""):
    """Print a formatted section header"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    if description:
        print(f"  {description}")
    print("=" * 70 + "\n")


def check_docker_service() -> bool:
    """Check if Docker service is running"""
    try:
        response = requests.get(f"{DOCKER_URL}/health", timeout=3)
        return response.status_code == 200
    except:
        return False


# ============================================================================
# REUSABLE HOOK LIBRARY (NEW in v0.7.5)
# ============================================================================


async def performance_optimization_hook(page, context, **kwargs):
    """
    Performance Hook: Block unnecessary resources to speed up crawling
    """
    print("  [Hook] 🚀 Optimizing performance - blocking images and ads...")

    # Block images
    await context.route(
        "**/*.{png,jpg,jpeg,gif,webp,svg,ico}", lambda route: route.abort()
    )

    # Block ads and analytics
    await context.route("**/analytics/*", lambda route: route.abort())
    await context.route("**/ads/*", lambda route: route.abort())
    await context.route("**/google-analytics.com/*", lambda route: route.abort())

    print("  [Hook] ✓ Performance optimization applied")
    return page


async def viewport_setup_hook(page, context, **kwargs):
    """
    Viewport Hook: Set consistent viewport size for rendering
    """
    print("  [Hook] 🖥️  Setting viewport to 1920x1080...")
    await page.set_viewport_size({"width": 1920, "height": 1080})
    print("  [Hook] ✓ Viewport configured")
    return page


async def authentication_headers_hook(page, context, url, **kwargs):
    """
    Headers Hook: Add custom authentication and tracking headers
    """
    print(f"  [Hook] 🔐 Adding custom headers for {url[:50]}...")

    await page.set_extra_http_headers(
        {
            "X-Crawl4AI-Version": "0.7.5",
            "X-Custom-Hook": "function-based-demo",
            "Accept-Language": "en-US,en;q=0.9",
            "User-Agent": "Crawl4AI/0.7.5 (Educational Demo)",
        }
    )

    print("  [Hook] ✓ Custom headers added")
    return page


async def lazy_loading_handler_hook(page, context, **kwargs):
    """
    Content Hook: Handle lazy-loaded content by scrolling
    """
    print("  [Hook] 📜 Scrolling to load lazy content...")

    # Scroll to bottom
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(1000)

    # Scroll to middle
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight / 2)")
    await page.wait_for_timeout(500)

    # Scroll back to top
    await page.evaluate("window.scrollTo(0, 0)")
    await page.wait_for_timeout(500)

    print("  [Hook] ✓ Lazy content loaded")
    return page


async def page_analytics_hook(page, context, **kwargs):
    """
    Analytics Hook: Log page metrics before extraction
    """
    print("  [Hook] 📊 Collecting page analytics...")

    metrics = await page.evaluate("""
        () => ({
            title: document.title,
            images: document.images.length,
            links: document.links.length,
            scripts: document.scripts.length,
            headings: document.querySelectorAll('h1, h2, h3').length,
            paragraphs: document.querySelectorAll('p').length
        })
    """)

    print(f"  [Hook] 📈 Page: {metrics['title'][:50]}...")
    print(
        f"         Links: {metrics['links']}, Images: {metrics['images']}, "
        f"Headings: {metrics['headings']}, Paragraphs: {metrics['paragraphs']}"
    )

    return page


# ============================================================================
# DEMO 1: String-Based Hooks (NEW Docker Hooks System)
# ============================================================================


def demo_1_string_based_hooks():
    """
    Demonstrate string-based hooks with REST API (part of NEW Docker Hooks System)
    """
    print_section(
        "DEMO 1: String-Based Hooks (REST API)",
        "Part of the NEW Docker Hooks System - hooks as strings",
    )

    # Define hooks as strings
    hooks_config = {
        "on_page_context_created": """
async def hook(page, context, **kwargs):
    print("  [String Hook] Setting up page context...")
    # Block images for performance
    await context.route("**/*.{png,jpg,jpeg,gif,webp}", lambda route: route.abort())
    await page.set_viewport_size({"width": 1920, "height": 1080})
    return page
""",
        "before_goto": """
async def hook(page, context, url, **kwargs):
    print(f"  [String Hook] Navigating to {url[:50]}...")
    await page.set_extra_http_headers({
        'X-Crawl4AI': 'string-based-hooks',
        'X-Demo': 'v0.7.5'
    })
    return page
""",
        "before_retrieve_html": """
async def hook(page, context, **kwargs):
    print("  [String Hook] Scrolling page...")
    await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
    await page.wait_for_timeout(1000)
    return page
""",
    }

    # Prepare request payload
    payload = {
        "urls": [TEST_URLS[0]],
        "hooks": {"code": hooks_config, "timeout": 30},
        "crawler_config": {"cache_mode": "bypass"},
    }

    print(f"🎯 Target URL: {TEST_URLS[0]}")
    print(f"🔧 Configured {len(hooks_config)} string-based hooks")
    print("📡 Sending request to Docker API...\n")

    try:
        start_time = time.time()
        response = requests.post(f"{DOCKER_URL}/crawl", json=payload, timeout=60)
        execution_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ Request successful! (took {execution_time:.2f}s)")

            # Display results
            if result.get("results") and result["results"][0].get("success"):
                crawl_result = result["results"][0]
                html_length = len(crawl_result.get("html", ""))
                markdown_length = len(crawl_result.get("markdown", ""))

                print("\n📊 Results:")
                print(f"   • HTML length: {html_length:,} characters")
                print(f"   • Markdown length: {markdown_length:,} characters")
                print(f"   • URL: {crawl_result.get('url')}")

                # Check hooks execution
                if "hooks" in result:
                    hooks_info = result["hooks"]
                    print("\n🎣 Hooks Execution:")
                    print(f"   • Status: {hooks_info['status']['status']}")
                    print(
                        f"   • Attached hooks: {len(hooks_info['status']['attached_hooks'])}"
                    )

                    if "summary" in hooks_info:
                        summary = hooks_info["summary"]
                        print(f"   • Total executions: {summary['total_executions']}")
                        print(f"   • Successful: {summary['successful']}")
                        print(f"   • Success rate: {summary['success_rate']:.1f}%")
            else:
                print("⚠️ Crawl completed but no results")

        else:
            print(f"❌ Request failed with status {response.status_code}")
            print(f"   Error: {response.text[:200]}")

    except requests.exceptions.Timeout:
        print("⏰ Request timed out after 60 seconds")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n" + "─" * 70)
    print("✓ String-based hooks demo complete\n")


# ============================================================================
# DEMO 2: Function-Based Hooks with hooks_to_string() Utility
# ============================================================================


def demo_2_hooks_to_string_utility():
    """
    Demonstrate the new hooks_to_string() utility for converting functions
    """
    print_section(
        "DEMO 2: hooks_to_string() Utility (NEW! ✨)",
        "Convert Python functions to strings for REST API",
    )

    print("📦 Creating hook functions...")
    print("   • performance_optimization_hook")
    print("   • viewport_setup_hook")
    print("   • authentication_headers_hook")
    print("   • lazy_loading_handler_hook")

    # Convert function objects to strings using the NEW utility
    print("\n🔄 Converting functions to strings with hooks_to_string()...")

    hooks_dict = {
        "on_page_context_created": performance_optimization_hook,
        "before_goto": authentication_headers_hook,
        "before_retrieve_html": lazy_loading_handler_hook,
    }

    hooks_as_strings = hooks_to_string(hooks_dict)

    print(f"✅ Successfully converted {len(hooks_as_strings)} functions to strings")

    # Show a preview
    print("\n📝 Sample converted hook (first 250 characters):")
    print("─" * 70)
    sample_hook = list(hooks_as_strings.values())[0]
    print(sample_hook[:250] + "...")
    print("─" * 70)

    # Use the converted hooks with REST API
    print("\n📡 Using converted hooks with REST API...")

    payload = {
        "urls": [TEST_URLS[0]],
        "hooks": {"code": hooks_as_strings, "timeout": 30},
    }

    try:
        start_time = time.time()
        response = requests.post(f"{DOCKER_URL}/crawl", json=payload, timeout=60)
        execution_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()
            print(f"\n✅ Request successful! (took {execution_time:.2f}s)")

            if result.get("results") and result["results"][0].get("success"):
                crawl_result = result["results"][0]
                print(
                    f"   • HTML length: {len(crawl_result.get('html', '')):,} characters"
                )
                print("   • Hooks executed successfully!")
        else:
            print(f"❌ Request failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n💡 Benefits of hooks_to_string():")
    print("   ✓ Write hooks as regular Python functions")
    print("   ✓ Full IDE support (autocomplete, syntax highlighting)")
    print("   ✓ Type checking and linting")
    print("   ✓ Easy to test and debug")
    print("   ✓ Reusable across projects")
    print("   ✓ Works with any REST API client")

    print("\n" + "─" * 70)
    print("✓ hooks_to_string() utility demo complete\n")


# ============================================================================
# DEMO 3: Docker Client with Automatic Conversion (RECOMMENDED! 🌟)
# ============================================================================


async def demo_3_docker_client_auto_conversion():
    """
    Demonstrate Docker Client with automatic hook conversion (RECOMMENDED)
    """
    print_section(
        "DEMO 3: Docker Client with Auto-Conversion (RECOMMENDED! 🌟)",
        "Pass function objects directly - conversion happens automatically!",
    )

    print("🐳 Initializing Crawl4AI Docker Client...")
    client = Crawl4aiDockerClient(base_url=DOCKER_URL)

    print("✅ Client ready!\n")

    # Use our reusable hook library - just pass the function objects!
    print("📚 Using reusable hook library:")
    print("   • performance_optimization_hook")
    print("   • viewport_setup_hook")
    print("   • authentication_headers_hook")
    print("   • lazy_loading_handler_hook")
    print("   • page_analytics_hook")

    print("\n🎯 Target URL: " + TEST_URLS[1])
    print("🚀 Starting crawl with automatic hook conversion...\n")

    try:
        start_time = time.time()

        # Pass function objects directly - NO manual conversion needed! ✨
        results = await client.crawl(
            urls=[TEST_URLS[0]],
            hooks={
                "on_page_context_created": performance_optimization_hook,
                "before_goto": authentication_headers_hook,
                "before_retrieve_html": lazy_loading_handler_hook,
                "before_return_html": page_analytics_hook,
            },
            hooks_timeout=30,
        )

        execution_time = time.time() - start_time

        print(f"\n✅ Crawl completed! (took {execution_time:.2f}s)\n")

        # Display results
        if results and results.success:
            result = results
            print("📊 Results:")
            print(f"   • URL: {result.url}")
            print(f"   • Success: {result.success}")
            print(f"   • HTML length: {len(result.html):,} characters")
            print(f"   • Markdown length: {len(result.markdown):,} characters")

            # Show metadata
            if result.metadata:
                print("\n📋 Metadata:")
                print(f"   • Title: {result.metadata.get('title', 'N/A')}")
                print(f"   • Description: {result.metadata.get('description', 'N/A')}")

            # Show links
            if result.links:
                internal_count = len(result.links.get("internal", []))
                external_count = len(result.links.get("external", []))
                print("\n🔗 Links Found:")
                print(f"   • Internal: {internal_count}")
                print(f"   • External: {external_count}")
        else:
            print("⚠️ Crawl completed but no successful results")
            if results:
                print(f"   Error: {results.error_message}")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()

    print("\n🌟 Why Docker Client is RECOMMENDED:")
    print("   ✓ Automatic function-to-string conversion")
    print("   ✓ No manual hooks_to_string() calls needed")
    print("   ✓ Cleaner, more Pythonic code")
    print("   ✓ Full type hints and IDE support")
    print("   ✓ Built-in error handling")
    print("   ✓ Async/await support")

    print("\n" + "─" * 70)
    print("✓ Docker Client auto-conversion demo complete\n")


# ============================================================================
# DEMO 4: Advanced Use Case - Complete Hook Pipeline
# ============================================================================


async def demo_4_complete_hook_pipeline():
    """
    Demonstrate a complete hook pipeline using all 8 hook points
    """
    print_section(
        "DEMO 4: Complete Hook Pipeline",
        "Using all 8 available hook points for comprehensive control",
    )

    # Define all 8 hooks
    async def on_browser_created_hook(browser, **kwargs):
        """Hook 1: Called after browser is created"""
        print("  [Pipeline] 1/8 Browser created")
        return browser

    async def on_page_context_created_hook(page, context, **kwargs):
        """Hook 2: Called after page context is created"""
        print("  [Pipeline] 2/8 Page context created - setting up...")
        await page.set_viewport_size({"width": 1920, "height": 1080})
        return page

    async def on_user_agent_updated_hook(page, context, user_agent, **kwargs):
        """Hook 3: Called when user agent is updated"""
        print(f"  [Pipeline] 3/8 User agent updated: {user_agent[:50]}...")
        return page

    async def before_goto_hook(page, context, url, **kwargs):
        """Hook 4: Called before navigating to URL"""
        print(f"  [Pipeline] 4/8 Before navigation to: {url[:60]}...")
        return page

    async def after_goto_hook(page, context, url, response, **kwargs):
        """Hook 5: Called after navigation completes"""
        print(
            f"  [Pipeline] 5/8 After navigation - Status: {response.status if response else 'N/A'}"
        )
        await page.wait_for_timeout(1000)
        return page

    async def on_execution_started_hook(page, context, **kwargs):
        """Hook 6: Called when JavaScript execution starts"""
        print("  [Pipeline] 6/8 JavaScript execution started")
        return page

    async def before_retrieve_html_hook(page, context, **kwargs):
        """Hook 7: Called before retrieving HTML"""
        print("  [Pipeline] 7/8 Before HTML retrieval - scrolling...")
        await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        return page

    async def before_return_html_hook(page, context, html, **kwargs):
        """Hook 8: Called before returning HTML"""
        print(f"  [Pipeline] 8/8 Before return - HTML length: {len(html):,} chars")
        return page

    print("🎯 Target URL: " + TEST_URLS[0])
    print("🔧 Configured ALL 8 hook points for complete pipeline control\n")

    client = Crawl4aiDockerClient(base_url=DOCKER_URL)

    try:
        print("🚀 Starting complete pipeline crawl...\n")
        start_time = time.time()

        results = await client.crawl(
            urls=[TEST_URLS[0]],
            hooks={
                "on_browser_created": on_browser_created_hook,
                "on_page_context_created": on_page_context_created_hook,
                "on_user_agent_updated": on_user_agent_updated_hook,
                "before_goto": before_goto_hook,
                "after_goto": after_goto_hook,
                "on_execution_started": on_execution_started_hook,
                "before_retrieve_html": before_retrieve_html_hook,
                "before_return_html": before_return_html_hook,
            },
            hooks_timeout=45,
        )

        execution_time = time.time() - start_time

        if results and results.success:
            print(
                f"\n✅ Complete pipeline executed successfully! (took {execution_time:.2f}s)"
            )
            print("   • All 8 hooks executed in sequence")
            print(f"   • HTML length: {len(results.html):,} characters")
        else:
            print("⚠️ Pipeline completed with warnings")

    except Exception as e:
        print(f"❌ Error: {str(e)}")

    print("\n📚 Available Hook Points:")
    print("   1. on_browser_created - Browser initialization")
    print("   2. on_page_context_created - Page context setup")
    print("   3. on_user_agent_updated - User agent configuration")
    print("   4. before_goto - Pre-navigation setup")
    print("   5. after_goto - Post-navigation processing")
    print("   6. on_execution_started - JavaScript execution start")
    print("   7. before_retrieve_html - Pre-extraction processing")
    print("   8. before_return_html - Final HTML processing")

    print("\n" + "─" * 70)
    print("✓ Complete hook pipeline demo complete\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """
    Run all demonstrations
    """
    print("\n" + "=" * 70)
    print("  🚀 Crawl4AI v0.7.5 - Docker Hooks Complete Demonstration")
    print("=" * 70)

    # Check Docker service
    print("\n🔍 Checking Docker service status...")
    if not check_docker_service():
        print("❌ Docker service is not running!")
        print("\n📋 To start the Docker service:")
        print("   docker run -p 11235:11235 unclecode/crawl4ai:latest")
        print("\nPlease start the service and run this demo again.")
        return

    print("✅ Docker service is running!\n")

    # Run all demos
    demos = [
        ("String-Based Hooks (REST API)", demo_1_string_based_hooks, False),
        ("hooks_to_string() Utility", demo_2_hooks_to_string_utility, False),
        ("Docker Client Auto-Conversion", demo_3_docker_client_auto_conversion, True),
        # ("Complete Hook Pipeline", demo_4_complete_hook_pipeline, True),
    ]

    for i, (name, demo_func, is_async) in enumerate(demos, 1):
        print(f"\n{'🔷' * 35}")
        print(f"Starting Demo {i}/{len(demos)}: {name}")
        print(f"{'🔷' * 35}\n")

        try:
            if is_async:
                await demo_func()
            else:
                demo_func()

            print(f"✅ Demo {i} completed successfully!")

            # Pause between demos (except the last one)
            if i < len(demos):
                print("\n⏸️  Press Enter to continue to next demo...")
                # input()

        except KeyboardInterrupt:
            print("\n⏹️  Demo interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Demo {i} failed: {str(e)}")
            import traceback

            traceback.print_exc()
            print("\nContinuing to next demo...\n")
            continue

    # Final summary
    print("\n" + "=" * 70)
    print("  🎉 All Demonstrations Complete!")
    print("=" * 70)

    print("\n📊 Summary of v0.7.5 Docker Hooks System:")
    print("\n🆕 COMPLETELY NEW FEATURE in v0.7.5:")
    print("   The Docker Hooks System lets you customize the crawling pipeline")
    print("   with user-provided Python functions at 8 strategic points.")

    print("\n✨ Three Ways to Use Docker Hooks (All NEW!):")
    print("   1. String-based - Write hooks as strings for REST API")
    print("   2. hooks_to_string() - Convert Python functions to strings")
    print("   3. Docker Client - Automatic conversion (RECOMMENDED)")

    print("\n💡 Key Benefits:")
    print("   ✓ Full IDE support (autocomplete, syntax highlighting)")
    print("   ✓ Type checking and linting")
    print("   ✓ Easy to test and debug")
    print("   ✓ Reusable across projects")
    print("   ✓ Complete pipeline control")

    print("\n🎯 8 Hook Points Available:")
    print("   • on_browser_created, on_page_context_created")
    print("   • on_user_agent_updated, before_goto, after_goto")
    print("   • on_execution_started, before_retrieve_html, before_return_html")

    print("\n📚 Resources:")
    print("   • Docs: https://docs.crawl4ai.com")
    print("   • GitHub: https://github.com/unclecode/crawl4ai")
    print("   • Discord: https://discord.gg/jP8KfhDhyN")

    print("\n" + "=" * 70)
    print("  Happy Crawling with v0.7.5! 🕷️")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print("\n🎬 Starting Crawl4AI v0.7.5 Docker Hooks Demonstration...")
    print("Press Ctrl+C anytime to exit\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user. Thanks for exploring Crawl4AI v0.7.5!")
    except Exception as e:
        print(f"\n\n❌ Demo error: {str(e)}")
        import traceback

        traceback.print_exc()
