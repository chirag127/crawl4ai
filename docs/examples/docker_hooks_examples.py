#!/usr/bin/env python3
"""
🚀 Crawl4AI Docker Hooks System - Complete Examples
====================================================

This file demonstrates the Docker Hooks System with three different approaches:

1. String-based hooks for REST API
2. hooks_to_string() utility to convert functions
3. Docker Client with automatic conversion (most convenient)

Requirements:
- Docker container running: docker run -p 11235:11235 unclecode/crawl4ai:latest
- crawl4ai installed: pip install crawl4ai
"""

import asyncio
import time

import requests

# Import Crawl4AI components
from crawl4ai import hooks_to_string
from crawl4ai.docker_client import Crawl4aiDockerClient

# Configuration
DOCKER_URL = "http://localhost:11235"
TEST_URLS = [
    "https://www.kidocode.com",
    "https://quotes.toscrape.com",
    "https://httpbin.org/html",
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
# REUSABLE HOOK LIBRARY
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
            "X-Crawl4AI": "docker-hooks",
            "X-Custom-Hook": "function-based",
            "Accept-Language": "en-US,en;q=0.9",
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
# APPROACH 1: String-Based Hooks (REST API)
# ============================================================================


def example_1_string_based_hooks():
    """
    Demonstrate string-based hooks with REST API
    Use this when working with REST API directly or non-Python clients
    """
    print_section(
        "APPROACH 1: String-Based Hooks (REST API)",
        "Define hooks as strings for REST API requests",
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
        "urls": [TEST_URLS[2]],  # httpbin.org
        "hooks": {"code": hooks_config, "timeout": 30},
        "crawler_config": {"cache_mode": "bypass"},
    }

    print(f"🎯 Target URL: {TEST_URLS[2]}")
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
    print("✓ String-based hooks example complete\n")


# ============================================================================
# APPROACH 2: Function-Based Hooks with hooks_to_string() Utility
# ============================================================================


def example_2_hooks_to_string_utility():
    """
    Demonstrate the hooks_to_string() utility for converting functions
    Use this when you want to write hooks as functions but use REST API
    """
    print_section(
        "APPROACH 2: hooks_to_string() Utility",
        "Convert Python functions to strings for REST API",
    )

    print("📦 Creating hook functions...")
    print("   • performance_optimization_hook")
    print("   • authentication_headers_hook")
    print("   • lazy_loading_handler_hook")

    # Convert function objects to strings using the utility
    print("\n🔄 Converting functions to strings with hooks_to_string()...")

    hooks_dict = {
        "on_page_context_created": performance_optimization_hook,
        "before_goto": authentication_headers_hook,
        "before_retrieve_html": lazy_loading_handler_hook,
    }

    hooks_as_strings = hooks_to_string(hooks_dict)

    print(f"✅ Successfully converted {len(hooks_as_strings)} functions to strings")

    # Show a preview
    print("\n📝 Sample converted hook (first 200 characters):")
    print("─" * 70)
    sample_hook = list(hooks_as_strings.values())[0]
    print(sample_hook[:200] + "...")
    print("─" * 70)

    # Use the converted hooks with REST API
    print("\n📡 Using converted hooks with REST API...")

    payload = {
        "urls": [TEST_URLS[2]],
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
    print("✓ hooks_to_string() utility example complete\n")


# ============================================================================
# APPROACH 3: Docker Client with Automatic Conversion (RECOMMENDED)
# ============================================================================


async def example_3_docker_client_auto_conversion():
    """
    Demonstrate Docker Client with automatic hook conversion (RECOMMENDED)
    Use this for the best developer experience with Python
    """
    print_section(
        "APPROACH 3: Docker Client with Auto-Conversion (RECOMMENDED)",
        "Pass function objects directly - conversion happens automatically!",
    )

    print("🐳 Initializing Crawl4AI Docker Client...")
    client = Crawl4aiDockerClient(base_url=DOCKER_URL)

    print("✅ Client ready!\n")

    # Use our reusable hook library - just pass the function objects!
    print("📚 Using reusable hook library:")
    print("   • performance_optimization_hook")
    print("   • authentication_headers_hook")
    print("   • lazy_loading_handler_hook")
    print("   • page_analytics_hook")

    print("\n🎯 Target URL: " + TEST_URLS[0])
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
                print(f"   • Title: {result.metadata.get('title', 'N/A')[:50]}...")

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
    print("✓ Docker Client auto-conversion example complete\n")


# ============================================================================
# APPROACH 4: Authentication Example
# ============================================================================


def example_4_authentication_flow():
    """
    Demonstrate authentication flow with multiple hooks
    """
    print_section(
        "EXAMPLE 4: Authentication Flow",
        "Using hooks for authentication with cookies and headers",
    )

    hooks_code = {
        "on_page_context_created": """
async def hook(page, context, **kwargs):
    print("[HOOK] Setting up authentication context")

    # Add authentication cookies
    await context.add_cookies([
        {
            "name": "auth_token",
            "value": "fake_jwt_token_here",
            "domain": ".httpbin.org",
            "path": "/",
            "httpOnly": True,
            "secure": True
        }
    ])

    return page
""",
        "before_goto": """
async def hook(page, context, url, **kwargs):
    print(f"[HOOK] Adding auth headers for {url}")

    # Add Authorization header
    import base64
    credentials = base64.b64encode(b"user:passwd").decode('ascii')

    await page.set_extra_http_headers({
        'Authorization': f'Basic {credentials}',
        'X-API-Key': 'test-api-key-123'
    })

    return page
""",
    }

    payload = {
        "urls": ["https://httpbin.org/basic-auth/user/passwd"],
        "hooks": {"code": hooks_code, "timeout": 15},
    }

    print("\nTesting authentication with httpbin endpoints...")
    response = requests.post(f"{DOCKER_URL}/crawl", json=payload)

    if response.status_code == 200:
        data = response.json()
        print("✅ Authentication test completed")

        if "results" in data:
            for i, result in enumerate(data["results"]):
                print(f"\n  URL {i+1}: {result['url']}")
                if result.get("success"):
                    # Check for authentication success indicators
                    html_content = result.get("html", "")
                    if '"authenticated"' in html_content and "true" in html_content:
                        print("    ✅ Authentication successful! Basic auth worked.")
                    else:
                        print("    ⚠️ Page loaded but auth status unclear")
                else:
                    print(
                        f"    ❌ Failed: {result.get('error_message', 'Unknown error')}"
                    )
    else:
        print(f"❌ Error: {response.status_code}")

    print("\n" + "─" * 70)
    print("✓ Authentication example complete\n")


# ============================================================================
# MAIN EXECUTION
# ============================================================================


async def main():
    """
    Run all example demonstrations
    """
    print("\n" + "=" * 70)
    print("  🚀 Crawl4AI - Docker Hooks System Examples")
    print("=" * 70)

    # Check Docker service
    print("\n🔍 Checking Docker service status...")
    if not check_docker_service():
        print("❌ Docker service is not running!")
        print("\n📋 To start the Docker service:")
        print("   docker run -p 11235:11235 unclecode/crawl4ai:latest")
        print("\nPlease start the service and run this example again.")
        return

    print("✅ Docker service is running!\n")

    # Run all examples
    examples = [
        ("String-Based Hooks (REST API)", example_1_string_based_hooks, False),
        ("hooks_to_string() Utility", example_2_hooks_to_string_utility, False),
        (
            "Docker Client Auto-Conversion (Recommended)",
            example_3_docker_client_auto_conversion,
            True,
        ),
        ("Authentication Flow", example_4_authentication_flow, False),
    ]

    for i, (name, example_func, is_async) in enumerate(examples, 1):
        print(f"\n{'🔷' * 35}")
        print(f"Example {i}/{len(examples)}: {name}")
        print(f"{'🔷' * 35}\n")

        try:
            if is_async:
                await example_func()
            else:
                example_func()

            print(f"✅ Example {i} completed successfully!")

            # Pause between examples (except the last one)
            if i < len(examples):
                print("\n⏸️  Press Enter to continue to next example...")
                input()

        except KeyboardInterrupt:
            print("\n⏹️  Examples interrupted by user")
            break
        except Exception as e:
            print(f"\n❌ Example {i} failed: {str(e)}")
            import traceback

            traceback.print_exc()
            print("\nContinuing to next example...\n")
            continue

    # Final summary
    print("\n" + "=" * 70)
    print("  🎉 All Examples Complete!")
    print("=" * 70)

    print("\n📊 Summary - Three Approaches to Docker Hooks:")

    print("\n✨ 1. String-Based Hooks:")
    print("   • Write hooks as strings directly in JSON")
    print("   • Best for: REST API, non-Python clients, simple use cases")
    print("   • Cons: No IDE support, harder to debug")

    print("\n✨ 2. hooks_to_string() Utility:")
    print("   • Write hooks as Python functions, convert to strings")
    print("   • Best for: Python with REST API, reusable hook libraries")
    print("   • Pros: IDE support, type checking, easy debugging")

    print("\n✨ 3. Docker Client (RECOMMENDED):")
    print("   • Pass function objects directly, automatic conversion")
    print("   • Best for: Python applications, best developer experience")
    print("   • Pros: All benefits of #2 + cleaner code, no manual conversion")

    print("\n💡 Recommendation:")
    print("   Use Docker Client (#3) for Python applications")
    print("   Use hooks_to_string() (#2) when you need REST API flexibility")
    print("   Use string-based (#1) for non-Python clients or simple scripts")

    print("\n🎯 8 Hook Points Available:")
    print("   • on_browser_created, on_page_context_created")
    print("   • on_user_agent_updated, before_goto, after_goto")
    print("   • on_execution_started, before_retrieve_html, before_return_html")

    print("\n📚 Resources:")
    print("   • Docs: https://docs.crawl4ai.com/core/docker-deployment")
    print("   • GitHub: https://github.com/unclecode/crawl4ai")
    print("   • Discord: https://discord.gg/jP8KfhDhyN")

    print("\n" + "=" * 70)
    print("  Happy Crawling! 🕷️")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    print("\n🎬 Starting Crawl4AI Docker Hooks Examples...")
    print("Press Ctrl+C anytime to exit\n")

    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Examples stopped by user. Thanks for exploring Crawl4AI!")
    except Exception as e:
        print(f"\n\n❌ Error: {str(e)}")
        import traceback

        traceback.print_exc()
