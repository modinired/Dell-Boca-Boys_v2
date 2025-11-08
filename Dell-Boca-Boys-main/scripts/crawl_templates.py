#!/usr/bin/env python3
"""
Crawl n8n workflow templates and add to knowledge base.
Fetches real-world examples from n8n template library.
"""
import sys
import os
import argparse

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.tools.crawler import crawler
from app.tools.memory import memory
from app.utils.logging import logger


TEMPLATE_URLS = [
    "https://n8n.io/workflows/",
    "https://n8n.io/integrations/",
]


def main():
    """Crawl n8n templates."""
    parser = argparse.ArgumentParser(description="Crawl n8n workflow templates")
    parser.add_argument(
        "--max-pages",
        type=int,
        default=50,
        help="Maximum pages to crawl (default: 50)"
    )
    parser.add_argument(
        "--url",
        type=str,
        help="Specific URL to crawl (optional)"
    )

    args = parser.parse_args()

    logger.info("Starting n8n template crawling", max_pages=args.max_pages)
    print(f"Crawling n8n templates (max {args.max_pages} pages)...")

    total_loaded = 0

    try:
        # Use specific URL if provided, otherwise use default list
        urls_to_crawl = [args.url] if args.url else TEMPLATE_URLS

        for start_url in urls_to_crawl:
            print(f"\nCrawling: {start_url}")

            try:
                pages = crawler.crawl_site(
                    start_url=start_url,
                    max_pages=args.max_pages // len(urls_to_crawl)
                )

                print(f"  Found {len(pages)} pages")

                # Add to knowledge base
                for page in pages:
                    try:
                        doc_id = memory.add_document(
                            content=page['content'],
                            source='templates',
                            title=page['title'],
                            url=page['url'],
                            meta={'crawled_from': start_url}
                        )
                        total_loaded += 1

                    except Exception as e:
                        logger.warning("Failed to add page", url=page['url'], error=str(e))

                print(f"  ✓ Loaded {len(pages)} templates")

            except Exception as e:
                logger.error("Failed to crawl URL", url=start_url, error=str(e))
                print(f"  ✗ Error crawling {start_url}: {e}")

        logger.info("Template crawling completed", total_loaded=total_loaded)
        print(f"\n✓ Total templates loaded: {total_loaded}")
        print(f"✓ Templates indexed and ready for semantic search")

        return 0

    except Exception as e:
        logger.error("Template crawling failed", error=str(e))
        print(f"\n✗ Crawling failed: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
