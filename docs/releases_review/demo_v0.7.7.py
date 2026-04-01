#!/usr/bin/env python3
"""
Crawl4AI v0.7.7 Release Demo
============================

This demo showcases the major feature in v0.7.7:
**Self-Hosting with Real-time Monitoring Dashboard**

Features Demonstrated:
1. System health monitoring with live metrics
2. Real-time request tracking (active & completed)
3. Browser pool management (permanent/hot/cold pools)
4. Monitor API endpoints for programmatic access
5. WebSocket streaming for real-time updates
6. Control actions (kill browser, cleanup, restart)
7. Production metrics (efficiency, reuse rates, memory)

Prerequisites:
- Crawl4AI Docker container running on localhost:11235
- Python packages: pip install httpx websockets

Usage:
python docs/releases_review/demo_v0.7.7.py
"""

import asyncio

import httpx

# Configuration
CRAWL4AI_BASE_URL = "http://localhost:11235"
MONITOR_DASHBOARD_URL = f"{CRAWL4AI_BASE_URL}/dashboard"


def print_section(title: str, description: str = ""):
    """Print a formatted section header"""
    print(f"\n{'=' * 70}")
    print(f"📊 {title}")
    if description:
        print(f"{description}")
    print(f"{'=' * 70}\n")


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-' * 70}")
    print(f"{title}")
    print(f"{'-' * 70}")


async def check_server_health():
    """Check if Crawl4AI server is running"""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{CRAWL4AI_BASE_URL}/health")
            return response.status_code == 200
    except:
        return False


async def demo_1_system_health_overview():
    """Demo 1: System Health Overview - Live metrics and pool status"""
    print_section(
        "Demo 1: System Health Overview",
        "Real-time monitoring of system resources and browser pool",
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔍 Fetching system health metrics...")

        try:
            response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/health")
            health = response.json()

            print("\n✅ System Health Report:")
            print("\n🖥️  Container Metrics:")
            print(f"   • CPU Usage: {health['container']['cpu_percent']:.1f}%")
            print(
                f"   • Memory Usage: {health['container']['memory_percent']:.1f}% "
                f"({health['container']['memory_mb']:.0f} MB)"
            )
            print(f"   • Network RX: {health['container']['network_rx_mb']:.2f} MB")
            print(f"   • Network TX: {health['container']['network_tx_mb']:.2f} MB")
            print(f"   • Uptime: {health['container']['uptime_seconds']:.0f}s")

            print("\n🌐 Browser Pool Status:")
            print("   Permanent Browser:")
            print(f"   • Active: {health['pool']['permanent']['active']}")
            print(
                f"   • Total Requests: {health['pool']['permanent']['total_requests']}"
            )

            print("   Hot Pool (Frequently Used Configs):")
            print(f"   • Count: {health['pool']['hot']['count']}")
            print(f"   • Total Requests: {health['pool']['hot']['total_requests']}")

            print("   Cold Pool (On-Demand Configs):")
            print(f"   • Count: {health['pool']['cold']['count']}")
            print(f"   • Total Requests: {health['pool']['cold']['total_requests']}")

            print("\n📈 Overall Statistics:")
            print(f"   • Total Requests: {health['stats']['total_requests']}")
            print(f"   • Success Rate: {health['stats']['success_rate_percent']:.1f}%")
            print(f"   • Avg Latency: {health['stats']['avg_latency_ms']:.0f}ms")

            print(f"\n💡 Dashboard URL: {MONITOR_DASHBOARD_URL}")

        except Exception as e:
            print(f"❌ Error fetching health: {e}")


async def demo_2_request_tracking():
    """Demo 2: Real-time Request Tracking - Generate and monitor requests"""
    print_section(
        "Demo 2: Real-time Request Tracking",
        "Submit crawl jobs and watch them in real-time",
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🚀 Submitting crawl requests...")

        # Submit multiple requests
        urls_to_crawl = [
            "https://httpbin.org/html",
            "https://httpbin.org/json",
            "https://example.com",
        ]

        tasks = []
        for url in urls_to_crawl:
            task = client.post(
                f"{CRAWL4AI_BASE_URL}/crawl", json={"urls": [url], "crawler_config": {}}
            )
            tasks.append(task)

        print(f"   • Submitting {len(urls_to_crawl)} requests in parallel...")
        results = await asyncio.gather(*tasks, return_exceptions=True)

        successful = sum(
            1 for r in results if not isinstance(r, Exception) and r.status_code == 200
        )
        print(f"   ✅ {successful}/{len(urls_to_crawl)} requests submitted")

        # Check request tracking
        print("\n📊 Checking request tracking...")
        await asyncio.sleep(2)  # Wait for requests to process

        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/requests")
        requests_data = response.json()

        print("\n📋 Request Status:")
        print(f"   • Active Requests: {len(requests_data['active'])}")
        print(f"   • Completed Requests: {len(requests_data['completed'])}")

        if requests_data["completed"]:
            print("\n📝 Recent Completed Requests:")
            for req in requests_data["completed"][:3]:
                status_icon = "✅" if req["success"] else "❌"
                print(f"   {status_icon} {req['endpoint']} - {req['latency_ms']:.0f}ms")


async def demo_3_browser_pool_management():
    """Demo 3: Browser Pool Management - 3-tier architecture in action"""
    print_section(
        "Demo 3: Browser Pool Management",
        "Understanding permanent, hot, and cold browser pools",
    )

    async with httpx.AsyncClient(timeout=60.0) as client:
        print("🌊 Testing browser pool with different configurations...")

        # Test 1: Default config (permanent browser)
        print("\n🔥 Test 1: Default Config → Permanent Browser")
        for i in range(3):
            await client.post(
                f"{CRAWL4AI_BASE_URL}/crawl",
                json={
                    "urls": [f"https://httpbin.org/html?req={i}"],
                    "crawler_config": {},
                },
            )
            print(f"   • Request {i+1}/3 sent (should use permanent browser)")

        await asyncio.sleep(2)

        # Test 2: Custom viewport (cold → hot promotion after 3 uses)
        print("\n♨️  Test 2: Custom Viewport → Cold Pool (promoting to Hot)")
        viewport_config = {"viewport": {"width": 1280, "height": 720}}
        for i in range(4):
            await client.post(
                f"{CRAWL4AI_BASE_URL}/crawl",
                json={
                    "urls": [f"https://httpbin.org/json?viewport={i}"],
                    "browser_config": viewport_config,
                    "crawler_config": {},
                },
            )
            print(f"   • Request {i+1}/4 sent (cold→hot promotion after 3rd use)")

        await asyncio.sleep(2)

        # Check browser pool status
        print("\n📊 Browser Pool Report:")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/browsers")
        browsers = response.json()

        print("\n🎯 Pool Summary:")
        print(f"   • Total Browsers: {browsers['summary']['total_count']}")
        print(f"   • Total Memory: {browsers['summary']['total_memory_mb']} MB")
        print(f"   • Reuse Rate: {browsers['summary']['reuse_rate_percent']:.1f}%")

        print("\n📋 Browser Pool Details:")
        if browsers["permanent"]:
            for browser in browsers["permanent"]:
                print(
                    f"   🔥 Permanent: {browser['browser_id'][:8]}... | "
                    f"Requests: {browser['request_count']} | "
                    f"Memory: {browser['memory_mb']:.0f} MB"
                )

        if browsers["hot"]:
            for browser in browsers["hot"]:
                print(
                    f"   ♨️  Hot: {browser['browser_id'][:8]}... | "
                    f"Requests: {browser['request_count']} | "
                    f"Memory: {browser['memory_mb']:.0f} MB"
                )

        if browsers["cold"]:
            for browser in browsers["cold"]:
                print(
                    f"   ❄️  Cold: {browser['browser_id'][:8]}... | "
                    f"Requests: {browser['request_count']} | "
                    f"Memory: {browser['memory_mb']:.0f} MB"
                )


async def demo_4_monitor_api_endpoints():
    """Demo 4: Monitor API Endpoints - Complete API surface"""
    print_section(
        "Demo 4: Monitor API Endpoints", "Programmatic access to all monitoring data"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🔌 Testing Monitor API endpoints...")

        # Endpoint performance statistics
        print_subsection("Endpoint Performance Statistics")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/endpoints/stats")
        endpoint_stats = response.json()

        print("\n📊 Per-Endpoint Analytics:")
        for endpoint, stats in endpoint_stats.items():
            print(f"   {endpoint}:")
            print(f"      • Requests: {stats['count']}")
            print(f"      • Avg Latency: {stats['avg_latency_ms']:.0f}ms")
            print(f"      • Success Rate: {stats['success_rate_percent']:.1f}%")

        # Timeline data for charts
        print_subsection("Timeline Data (for Charts)")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/timeline?minutes=5")
        timeline = response.json()

        print("\n📈 Timeline Metrics (last 5 minutes):")
        print(f"   • Data Points: {len(timeline['memory'])}")
        if timeline["memory"]:
            latest = timeline["memory"][-1]
            print(f"   • Latest Memory: {latest['value']:.1f}%")
            print(f"   • Timestamp: {latest['timestamp']}")

        # Janitor logs
        print_subsection("Janitor Cleanup Events")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/logs/janitor?limit=3")
        janitor_logs = response.json()

        print("\n🧹 Recent Cleanup Activities:")
        if janitor_logs:
            for log in janitor_logs[:3]:
                print(f"   • {log['timestamp']}: {log['message']}")
        else:
            print("   (No cleanup events yet - janitor runs periodically)")

        # Error logs
        print_subsection("Error Monitoring")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/logs/errors?limit=3")
        error_logs = response.json()

        print("\n❌ Recent Errors:")
        if error_logs:
            for log in error_logs[:3]:
                print(f"   • {log['timestamp']}: {log['error_type']}")
                print(f"     {log['message'][:100]}...")
        else:
            print("   ✅ No recent errors!")


async def demo_5_websocket_streaming():
    """Demo 5: WebSocket Streaming - Real-time updates"""
    print_section(
        "Demo 5: WebSocket Streaming", "Live monitoring with 2-second update intervals"
    )

    print("⚡ WebSocket Streaming Demo")
    print("\n💡 The monitoring dashboard uses WebSocket for real-time updates")
    print("   • Connection: ws://localhost:11235/monitor/ws")
    print("   • Update Interval: 2 seconds")
    print("   • Data: Health, requests, browsers, memory, errors")

    print("\n📝 Sample WebSocket Integration Code:")
    print("""
    import websockets
    import json

    async def monitor_realtime():
        uri = "ws://localhost:11235/monitor/ws"
        async with websockets.connect(uri) as websocket:
            while True:
                data = await websocket.recv()
                update = json.loads(data)

                print(f"Memory: {update['health']['container']['memory_percent']:.1f}%")
                print(f"Active Requests: {len(update['requests']['active'])}")
                print(f"Browser Pool: {update['health']['pool']['permanent']['active']}")
    """)

    print("\n🌐 Open the dashboard to see WebSocket in action:")
    print(f"   {MONITOR_DASHBOARD_URL}")


async def demo_6_control_actions():
    """Demo 6: Control Actions - Manual browser management"""
    print_section(
        "Demo 6: Control Actions", "Manual control over browser pool and cleanup"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("🎮 Testing control actions...")

        # Force cleanup
        print_subsection("Force Immediate Cleanup")
        print("🧹 Triggering manual cleanup...")
        try:
            response = await client.post(f"{CRAWL4AI_BASE_URL}/monitor/actions/cleanup")
            if response.status_code == 200:
                result = response.json()
                print("   ✅ Cleanup completed")
                print(f"   • Browsers cleaned: {result.get('cleaned_count', 0)}")
                print(f"   • Memory freed: {result.get('memory_freed_mb', 0):.1f} MB")
            else:
                print(f"   ⚠️  Response: {response.status_code}")
        except Exception as e:
            print(f"   ℹ️  Cleanup action: {e}")

        # Get browser list for potential kill/restart
        print_subsection("Browser Management")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/browsers")
        browsers = response.json()

        cold_browsers = browsers.get("cold", [])
        if cold_browsers:
            browser_id = cold_browsers[0]["browser_id"]
            print("\n🎯 Example: Kill specific browser")
            print("   POST /monitor/actions/kill_browser")
            print(f"   JSON: {{'browser_id': '{browser_id[:16]}...'}}")
            print("   → Kills the browser and frees resources")

        print("\n🔄 Example: Restart browser")
        print("   POST /monitor/actions/restart_browser")
        print("   JSON: {'browser_id': 'browser_id_here'}")
        print("   → Restart a specific browser instance")

        # Reset statistics
        print_subsection("Reset Statistics")
        print("📊 Statistics can be reset for fresh monitoring:")
        print("   POST /monitor/stats/reset")
        print("   → Clears all accumulated statistics")


async def demo_7_production_metrics():
    """Demo 7: Production Metrics - Key indicators for operations"""
    print_section(
        "Demo 7: Production Metrics", "Critical metrics for production monitoring"
    )

    async with httpx.AsyncClient(timeout=30.0) as client:
        print("📊 Key Production Metrics:")

        # Overall health
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/health")
        health = response.json()

        # Browser efficiency
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/browsers")
        browsers = response.json()

        print("\n🎯 Critical Metrics to Track:")

        print("\n1️⃣  Memory Usage Trends")
        print(f"   • Current: {health['container']['memory_percent']:.1f}%")
        print("   • Alert if: >80%")
        print("   • Action: Trigger cleanup or scale")

        print("\n2️⃣  Request Success Rate")
        print(f"   • Current: {health['stats']['success_rate_percent']:.1f}%")
        print("   • Target: >95%")
        print("   • Alert if: <90%")

        print("\n3️⃣  Average Latency")
        print(f"   • Current: {health['stats']['avg_latency_ms']:.0f}ms")
        print("   • Target: <2000ms")
        print("   • Alert if: >5000ms")

        print("\n4️⃣  Browser Pool Efficiency")
        print(f"   • Reuse Rate: {browsers['summary']['reuse_rate_percent']:.1f}%")
        print("   • Target: >80%")
        print("   • Indicates: Effective browser pooling")

        print("\n5️⃣  Total Browsers")
        print(f"   • Current: {browsers['summary']['total_count']}")
        print("   • Alert if: >20 (possible leak)")
        print("   • Check: Janitor is running correctly")

        print("\n6️⃣  Error Frequency")
        response = await client.get(f"{CRAWL4AI_BASE_URL}/monitor/logs/errors?limit=10")
        errors = response.json()
        print(f"   • Recent Errors: {len(errors)}")
        print("   • Alert if: >10 in last hour")
        print("   • Action: Review error patterns")

        print("\n💡 Integration Examples:")
        print("   • Prometheus: Scrape /monitor/health")
        print("   • Alerting: Monitor memory, success rate, latency")
        print("   • Dashboards: WebSocket streaming to custom UI")
        print("   • Log Aggregation: Collect /monitor/logs/* endpoints")


async def demo_8_self_hosting_value():
    """Demo 8: Self-Hosting Value Proposition"""
    print_section(
        "Demo 8: Why Self-Host Crawl4AI?",
        "The value proposition of owning your infrastructure",
    )

    print("🎯 Self-Hosting Benefits:\n")

    print("🔒 Data Privacy & Security")
    print("   • Your data never leaves your infrastructure")
    print("   • No third-party access to crawled content")
    print("   • Keep sensitive workflows behind your firewall")

    print("\n💰 Cost Control")
    print("   • No per-request pricing or rate limits")
    print("   • Predictable infrastructure costs")
    print("   • Scale based on your actual needs")

    print("\n🎯 Full Customization")
    print("   • Complete control over browser configs")
    print("   • Custom hooks and strategies")
    print("   • Tailored monitoring and alerting")

    print("\n📊 Complete Transparency")
    print("   • Real-time monitoring dashboard")
    print("   • Full visibility into system performance")
    print("   • Detailed request and error tracking")

    print("\n⚡ Performance & Flexibility")
    print("   • Direct access, no network overhead")
    print("   • Integrate with existing infrastructure")
    print("   • Custom resource allocation")

    print("\n🛡️ Enterprise-Grade Operations")
    print("   • Prometheus integration ready")
    print("   • WebSocket for real-time dashboards")
    print("   • Full API for automation")
    print("   • Manual controls for troubleshooting")

    print("\n🌐 Get Started:")
    print("   docker pull unclecode/crawl4ai:0.7.7")
    print("   docker run -d -p 11235:11235 --shm-size=1g unclecode/crawl4ai:0.7.7")
    print(f"   # Visit: {MONITOR_DASHBOARD_URL}")


def print_summary():
    """Print comprehensive demo summary"""
    print("\n" + "=" * 70)
    print("📊 DEMO SUMMARY - Crawl4AI v0.7.7")
    print("=" * 70)

    print("\n✨ Features Demonstrated:")
    print("=" * 70)
    print("✅ System Health Overview")
    print("   → Real-time CPU, memory, network, and uptime monitoring")

    print("\n✅ Request Tracking")
    print("   → Active and completed request monitoring with full details")

    print("\n✅ Browser Pool Management")
    print("   → 3-tier architecture: Permanent, Hot, and Cold pools")
    print("   → Automatic promotion and cleanup")

    print("\n✅ Monitor API Endpoints")
    print("   → Complete REST API for programmatic access")
    print("   → Health, requests, browsers, timeline, logs, errors")

    print("\n✅ WebSocket Streaming")
    print("   → Real-time updates every 2 seconds")
    print("   → Build custom dashboards with live data")

    print("\n✅ Control Actions")
    print("   → Manual browser management (kill, restart)")
    print("   → Force cleanup and statistics reset")

    print("\n✅ Production Metrics")
    print("   → 6 critical metrics for operational excellence")
    print("   → Prometheus integration patterns")

    print("\n✅ Self-Hosting Value")
    print("   → Data privacy, cost control, full customization")
    print("   → Enterprise-grade transparency and control")

    print("\n" + "=" * 70)
    print("🎯 What's New in v0.7.7?")
    print("=" * 70)
    print("• 📊 Complete Real-time Monitoring System")
    print("• 🌐 Interactive Web Dashboard (/dashboard)")
    print("• 🔌 Comprehensive Monitor API")
    print("• ⚡ WebSocket Streaming (2-second updates)")
    print("• 🎮 Manual Control Actions")
    print("• 📈 Production Integration Examples")
    print("• 🏭 Prometheus, Alerting, Log Aggregation")
    print("• 🔥 Smart Browser Pool (Permanent/Hot/Cold)")
    print("• 🧹 Automatic Janitor Cleanup")
    print("• 📋 Full Request & Error Tracking")

    print("\n" + "=" * 70)
    print("💡 Why This Matters")
    print("=" * 70)
    print("Before v0.7.7: Docker was just a containerized crawler")
    print("After v0.7.7: Complete self-hosting platform with enterprise monitoring")
    print("\nYou now have:")
    print("  • Full visibility into what's happening inside")
    print("  • Real-time operational dashboards")
    print("  • Complete control over browser resources")
    print("  • Production-ready observability")
    print("  • Zero external dependencies")

    print("\n" + "=" * 70)
    print("📚 Next Steps")
    print("=" * 70)
    print(f"1. Open the dashboard: {MONITOR_DASHBOARD_URL}")
    print("2. Read the docs: https://docs.crawl4ai.com/basic/self-hosting/")
    print("3. Try the Monitor API endpoints yourself")
    print("4. Set up Prometheus integration for production")
    print("5. Build custom dashboards with WebSocket streaming")

    print("\n" + "=" * 70)
    print("🔗 Resources")
    print("=" * 70)
    print(f"• Dashboard: {MONITOR_DASHBOARD_URL}")
    print(f"• Health API: {CRAWL4AI_BASE_URL}/monitor/health")
    print("• Documentation: https://docs.crawl4ai.com/")
    print("• GitHub: https://github.com/unclecode/crawl4ai")

    print("\n" + "=" * 70)
    print("🎉 You're now in control of your web crawling destiny!")
    print("=" * 70)


async def main():
    """Run all demos"""
    print("\n" + "=" * 70)
    print("🚀 Crawl4AI v0.7.7 Release Demo")
    print("=" * 70)
    print("Feature: Self-Hosting with Real-time Monitoring Dashboard")
    print("=" * 70)

    # Check if server is running
    print("\n🔍 Checking Crawl4AI server...")
    server_running = await check_server_health()

    if not server_running:
        print(f"❌ Cannot connect to Crawl4AI at {CRAWL4AI_BASE_URL}")
        print("\nPlease start the Docker container:")
        print("  docker pull unclecode/crawl4ai:0.7.7")
        print("  docker run -d -p 11235:11235 --shm-size=1g unclecode/crawl4ai:0.7.7")
        print("\nThen re-run this demo.")
        return

    print("✅ Crawl4AI server is running!")
    print(f"📊 Dashboard available at: {MONITOR_DASHBOARD_URL}")

    # Run all demos
    demos = [
        demo_1_system_health_overview,
        demo_2_request_tracking,
        demo_3_browser_pool_management,
        demo_4_monitor_api_endpoints,
        demo_5_websocket_streaming,
        demo_6_control_actions,
        demo_7_production_metrics,
        demo_8_self_hosting_value,
    ]

    for i, demo_func in enumerate(demos, 1):
        try:
            await demo_func()

            if i < len(demos):
                await asyncio.sleep(2)  # Brief pause between demos

        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
            return
        except Exception as e:
            print(f"\n❌ Demo {i} error: {e}")
            print("Continuing to next demo...\n")
            continue

    # Print comprehensive summary
    print_summary()

    print("\n" + "=" * 70)
    print("✅ Demo completed!")
    print("=" * 70)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Demo stopped by user. Thanks for trying Crawl4AI v0.7.7!")
    except Exception as e:
        print(f"\n\n❌ Demo failed: {e}")
        print("Make sure the Docker container is running:")
        print("  docker run -d -p 11235:11235 --shm-size=1g unclecode/crawl4ai:0.7.7")
