#!/usr/bin/env python3
"""
Link Head Extraction & Scoring Example

This example demonstrates Crawl4AI's advanced link analysis capabilities:
1. Basic link head extraction
2. Three-layer scoring system (intrinsic, contextual, total)
3. Pattern-based filtering
4. Multiple practical use cases

Requirements:
- crawl4ai installed
- Internet connection

Usage:
    python link_head_extraction_example.py
"""

import asyncio

from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LinkPreviewConfig


async def basic_link_head_extraction():
    """
    Basic example: Extract head content from internal links with scoring
    """
    print("🔗 Basic Link Head Extraction Example")
    print("=" * 50)

    config = CrawlerRunConfig(
        # Enable link head extraction
        link_preview_config=LinkPreviewConfig(
            include_internal=True,  # Process internal links
            include_external=False,  # Skip external links for this demo
            max_links=5,  # Limit to 5 links
            concurrency=3,  # Process 3 links simultaneously
            timeout=10,  # 10 second timeout per link
            query="API documentation guide",  # Query for relevance scoring
            verbose=True,  # Show detailed progress
        ),
        # Enable intrinsic link scoring
        score_links=True,
        only_text=True,
    )

    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://docs.python.org/3/", config=config)

        if result.success:
            print(f"\n✅ Successfully crawled: {result.url}")

            internal_links = result.links.get("internal", [])
            links_with_head = [
                link for link in internal_links if link.get("head_data") is not None
            ]

            print(f"🧠 Links with head data: {len(links_with_head)}")

            # Show detailed results
            for i, link in enumerate(links_with_head[:3]):
                print(f"\n📄 Link {i+1}: {link['href']}")
                print(f"   Text: '{link.get('text', 'No text')[:50]}...'")

                # Show all three score types
                intrinsic = link.get("intrinsic_score")
                contextual = link.get("contextual_score")
                total = link.get("total_score")

                print("   📊 Scores:")
                if intrinsic is not None:
                    print(f"      • Intrinsic: {intrinsic:.2f}/10.0")
                if contextual is not None:
                    print(f"      • Contextual: {contextual:.3f}")
                if total is not None:
                    print(f"      • Total: {total:.3f}")

                # Show head data
                head_data = link.get("head_data", {})
                if head_data:
                    title = head_data.get("title", "No title")
                    description = head_data.get("meta", {}).get("description", "")
                    print(f"   📰 Title: {title[:60]}...")
                    if description:
                        print(f"   📝 Description: {description[:80]}...")
        else:
            print(f"❌ Crawl failed: {result.error_message}")


async def research_assistant_example():
    """
    Research Assistant: Find highly relevant documentation pages
    """
    print("\n\n🔍 Research Assistant Example")
    print("=" * 50)

    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            include_external=True,
            include_patterns=["*/docs/*", "*/tutorial/*", "*/guide/*"],
            exclude_patterns=["*/login*", "*/admin*"],
            query="machine learning neural networks deep learning",
            max_links=15,
            score_threshold=0.4,  # Only include high-relevance links
            concurrency=8,
            verbose=False,  # Clean output for this example
        ),
        score_links=True,
    )

    # Test with scikit-learn documentation
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://scikit-learn.org/stable/", config=config)

        if result.success:
            print(f"✅ Analyzed: {result.url}")

            all_links = result.links.get("internal", []) + result.links.get(
                "external", []
            )

            # Filter for high-scoring links
            high_scoring_links = [
                link for link in all_links if link.get("total_score", 0) > 0.6
            ]

            # Sort by total score (highest first)
            high_scoring_links.sort(key=lambda x: x.get("total_score", 0), reverse=True)

            print(f"\n🎯 Found {len(high_scoring_links)} highly relevant links:")
            print("   (Showing top 5 by relevance score)")

            for i, link in enumerate(high_scoring_links[:5]):
                score = link.get("total_score", 0)
                title = link.get("head_data", {}).get("title", "No title")
                print(f"\n{i+1}. ⭐ {score:.3f} - {title[:70]}...")
                print(f"   🔗 {link['href']}")

                # Show score breakdown
                intrinsic = link.get("intrinsic_score", 0)
                contextual = link.get("contextual_score", 0)
                print(
                    f"   📊 Quality: {intrinsic:.1f}/10 | Relevance: {contextual:.3f}"
                )
        else:
            print(f"❌ Research failed: {result.error_message}")


async def api_discovery_example():
    """
    API Discovery: Find API endpoints and references
    """
    print("\n\n🔧 API Discovery Example")
    print("=" * 50)

    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            include_patterns=["*/api/*", "*/reference/*", "*/endpoint/*"],
            exclude_patterns=["*/deprecated/*", "*/v1/*"],  # Skip old versions
            max_links=25,
            concurrency=10,
            timeout=8,
            verbose=False,
        ),
        score_links=True,
    )

    # Example with a documentation site that has API references
    async with AsyncWebCrawler() as crawler:
        result = await crawler.arun("https://httpbin.org/", config=config)

        if result.success:
            print(f"✅ Discovered APIs at: {result.url}")

            api_links = result.links.get("internal", [])

            # Categorize by detected content
            endpoints = {"GET": [], "POST": [], "PUT": [], "DELETE": [], "OTHER": []}

            for link in api_links:
                if link.get("head_data"):
                    title = link.get("head_data", {}).get("title", "").upper()
                    text = link.get("text", "").upper()

                    # Simple categorization based on content
                    if "GET" in title or "GET" in text:
                        endpoints["GET"].append(link)
                    elif "POST" in title or "POST" in text:
                        endpoints["POST"].append(link)
                    elif "PUT" in title or "PUT" in text:
                        endpoints["PUT"].append(link)
                    elif "DELETE" in title or "DELETE" in text:
                        endpoints["DELETE"].append(link)
                    else:
                        endpoints["OTHER"].append(link)

            # Display results
            total_found = sum(len(links) for links in endpoints.values())
            print(f"\n📡 Found {total_found} API-related links:")

            for method, links in endpoints.items():
                if links:
                    print(f"\n{method} Endpoints ({len(links)}):")
                    for link in links[:3]:  # Show first 3 of each type
                        title = link.get("head_data", {}).get("title", "No title")
                        score = link.get("intrinsic_score", 0)
                        print(f"  • [{score:.1f}] {title[:50]}...")
                        print(f"    {link['href']}")
        else:
            print(f"❌ API discovery failed: {result.error_message}")


async def link_quality_analysis():
    """
    Link Quality Analysis: Analyze website structure and link quality
    """
    print("\n\n📊 Link Quality Analysis Example")
    print("=" * 50)

    config = CrawlerRunConfig(
        link_preview_config=LinkPreviewConfig(
            include_internal=True,
            max_links=30,  # Analyze more links for better statistics
            concurrency=15,
            timeout=6,
            verbose=False,
        ),
        score_links=True,
    )

    async with AsyncWebCrawler() as crawler:
        # Test with a content-rich site
        result = await crawler.arun("https://docs.python.org/3/", config=config)

        if result.success:
            print(f"✅ Analyzed: {result.url}")

            links = result.links.get("internal", [])

            # Extract intrinsic scores for analysis
            scores = [
                link.get("intrinsic_score", 0)
                for link in links
                if link.get("intrinsic_score") is not None
            ]

            if scores:
                avg_score = sum(scores) / len(scores)
                high_quality = len([s for s in scores if s >= 7.0])
                medium_quality = len([s for s in scores if 4.0 <= s < 7.0])
                low_quality = len([s for s in scores if s < 4.0])

                print("\n📈 Quality Analysis Results:")
                print(f"   📊 Average Score: {avg_score:.2f}/10.0")
                print(f"   🟢 High Quality (≥7.0): {high_quality} links")
                print(f"   🟡 Medium Quality (4.0-6.9): {medium_quality} links")
                print(f"   🔴 Low Quality (<4.0): {low_quality} links")

                # Show best and worst links
                scored_links = [
                    (link, link.get("intrinsic_score", 0))
                    for link in links
                    if link.get("intrinsic_score") is not None
                ]
                scored_links.sort(key=lambda x: x[1], reverse=True)

                print("\n🏆 Top 3 Quality Links:")
                for i, (link, score) in enumerate(scored_links[:3]):
                    text = link.get("text", "No text")[:40]
                    print(f"   {i+1}. [{score:.1f}] {text}...")
                    print(f"      {link['href']}")

                print("\n⚠️  Bottom 3 Quality Links:")
                for i, (link, score) in enumerate(scored_links[-3:]):
                    text = link.get("text", "No text")[:40]
                    print(f"   {i+1}. [{score:.1f}] {text}...")
                    print(f"      {link['href']}")
            else:
                print("❌ No scoring data available")
        else:
            print(f"❌ Analysis failed: {result.error_message}")


async def pattern_filtering_example():
    """
    Pattern Filtering: Demonstrate advanced filtering capabilities
    """
    print("\n\n🎯 Pattern Filtering Example")
    print("=" * 50)

    # Example with multiple filtering strategies
    filters = [
        {
            "name": "Documentation Only",
            "config": LinkPreviewConfig(
                include_internal=True,
                max_links=10,
                concurrency=5,
                verbose=False,
                include_patterns=["*/docs/*", "*/documentation/*"],
                exclude_patterns=["*/api/*"],
            ),
        },
        {
            "name": "API References Only",
            "config": LinkPreviewConfig(
                include_internal=True,
                max_links=10,
                concurrency=5,
                verbose=False,
                include_patterns=["*/api/*", "*/reference/*"],
                exclude_patterns=["*/tutorial/*"],
            ),
        },
        {
            "name": "Exclude Admin Areas",
            "config": LinkPreviewConfig(
                include_internal=True,
                max_links=10,
                concurrency=5,
                verbose=False,
                exclude_patterns=["*/admin/*", "*/login/*", "*/dashboard/*"],
            ),
        },
    ]

    async with AsyncWebCrawler() as crawler:
        for filter_example in filters:
            print(f"\n🔍 Testing: {filter_example['name']}")

            config = CrawlerRunConfig(
                link_preview_config=filter_example["config"], score_links=True
            )

            result = await crawler.arun("https://docs.python.org/3/", config=config)

            if result.success:
                links = result.links.get("internal", [])
                links_with_head = [link for link in links if link.get("head_data")]

                print(f"   📊 Found {len(links_with_head)} matching links")

                if links_with_head:
                    # Show sample matches
                    for link in links_with_head[:2]:
                        title = link.get("head_data", {}).get("title", "No title")
                        print(f"   • {title[:50]}...")
                        print(f"     {link['href']}")
            else:
                print(f"   ❌ Failed: {result.error_message}")


async def main():
    """
    Run all examples
    """
    print("🚀 Crawl4AI Link Head Extraction Examples")
    print("=" * 60)
    print("This will demonstrate various link analysis capabilities.\n")

    try:
        # Run all examples
        await basic_link_head_extraction()
        await research_assistant_example()
        await api_discovery_example()
        await link_quality_analysis()
        await pattern_filtering_example()

        print("\n" + "=" * 60)
        print("✨ All examples completed successfully!")
        print("\nNext steps:")
        print("1. Try modifying the queries and patterns above")
        print("2. Test with your own websites")
        print("3. Experiment with different score thresholds")
        print("4. Check out the full documentation for more options")

    except KeyboardInterrupt:
        print("\n⏹️  Examples interrupted by user")
    except Exception as e:
        print(f"\n💥 Error running examples: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
