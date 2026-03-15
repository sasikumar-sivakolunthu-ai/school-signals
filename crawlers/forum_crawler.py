"""
Forum crawler for school admissions forums.

Reads active forum sources from the `sources` table (platform='forum',
access_method='webscrape'), crawls threads and posts, and stores raw content
in the `documents` table for the agent pipeline to process.

Supported forums:
  - Mumsnet (mumsnet.com)
  - The Student Room (thestudentroom.co.uk)
  - Netmums (netmums.com)

Usage:
  python crawlers/forum_crawler.py
  python crawlers/forum_crawler.py --source-id <uuid>   # single source
  python crawlers/forum_crawler.py --dry-run            # no DB writes
"""

import argparse
import hashlib
import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Optional
from urllib.parse import urljoin, urlparse

import httpx
import psycopg2
import psycopg2.extras
from bs4 import BeautifulSoup
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("forum_crawler")

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (compatible; SchoolSignalBot/1.0; "
        "+https://github.com/school-signal)"
    ),
    "Accept-Language": "en-GB,en;q=0.9",
}

RATE_LIMIT_SECONDS = float(os.getenv("CRAWL_RATE_LIMIT", "2.0"))
MAX_THREADS_PER_SOURCE = int(os.getenv("MAX_THREADS_PER_SOURCE", "20"))
MAX_POSTS_PER_THREAD = int(os.getenv("MAX_POSTS_PER_THREAD", "100"))
REQUEST_TIMEOUT = int(os.getenv("REQUEST_TIMEOUT", "30"))


# ---------------------------------------------------------------------------
# Database helpers
# ---------------------------------------------------------------------------


def get_db_connection():
    url = os.getenv("DATABASE_URL")
    if not url:
        raise EnvironmentError(
            "DATABASE_URL not set. "
            "Set it to your Supabase direct Postgres connection string:\n"
            "  postgresql://postgres:<password>@db.<project>.supabase.co:5432/postgres"
        )
    conn = psycopg2.connect(url)
    conn.autocommit = False
    return conn


def load_forum_sources(conn, source_id: Optional[str] = None) -> list[dict]:
    """Return active forum sources that use webscraping."""
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # Known forum platform values in platform_enum
    if source_id:
        cur.execute(
            """
            SELECT s.id, s.school_id, s.source_name, s.url, s.trust_base_score,
                   sc.name AS school_name
            FROM sources s
            LEFT JOIN schools sc ON sc.id = s.school_id
            WHERE s.id = %s
            """,
            (source_id,),
        )
    else:
        cur.execute(
            """
            SELECT s.id, s.school_id, s.source_name, s.url, s.trust_base_score,
                   sc.name AS school_name
            FROM sources s
            LEFT JOIN schools sc ON sc.id = s.school_id
            WHERE s.active = true
              AND s.access_method::text = 'webscrape'
            ORDER BY s.updated_at DESC
            """
        )
    rows = cur.fetchall()
    cur.close()
    return [dict(r) for r in rows]


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def document_exists(conn, chash: str) -> bool:
    cur = conn.cursor()
    cur.execute(
        "SELECT 1 FROM documents WHERE metadata->>'content_hash' = %s LIMIT 1",
        (chash,),
    )
    exists = cur.fetchone() is not None
    cur.close()
    return exists


def insert_document(conn, source_id: str, doc_type: str, raw_content: str, metadata: dict):
    chash = content_hash(raw_content)
    if document_exists(conn, chash):
        log.debug("Skip duplicate: %s", metadata.get("url", ""))
        return False

    metadata["content_hash"] = chash
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO documents (source_id, document_type, raw_content, metadata, crawled_at)
        VALUES (%s, %s::document_type_enum, %s, %s, %s)
        """,
        (
            source_id,
            doc_type,
            raw_content,
            json.dumps(metadata),
            datetime.now(timezone.utc),
        ),
    )
    cur.close()
    return True


# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------


def fetch(client: httpx.Client, url: str) -> Optional[BeautifulSoup]:
    try:
        resp = client.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        return BeautifulSoup(resp.text, "html.parser")
    except httpx.HTTPStatusError as e:
        log.warning("HTTP %s fetching %s", e.response.status_code, url)
    except Exception as e:
        log.warning("Error fetching %s: %s", url, e)
    return None


# ---------------------------------------------------------------------------
# Forum parsers
# ---------------------------------------------------------------------------


class MumsnetParser:
    """
    Crawls Mumsnet discussion threads.
    Expects the source URL to be a topic/search page, e.g.:
      https://www.mumsnet.com/Talk/secondary_education?keywords=waiting+list
    """

    DOMAIN = "mumsnet.com"

    def thread_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        for a in soup.select("a[href]"):
            href = a["href"]
            if "/Talk/" in href and href.count("/") >= 3:
                full = urljoin(base_url, href).split("?")[0]
                if full not in links:
                    links.append(full)
        return links[:MAX_THREADS_PER_SOURCE]

    def parse_thread(self, soup: BeautifulSoup, thread_url: str) -> list[dict]:
        posts = []
        title_el = soup.select_one("h1")
        thread_title = title_el.get_text(strip=True) if title_el else ""

        for post_el in soup.select("[data-testid='thread-op'], [data-testid='talk-post']"):
            author_el = post_el.select_one("[data-testid='talk-post-nickname'], .nickname")
            date_el = post_el.select_one("time")
            body_el = post_el.select_one(".talk-post-message, p")

            text = body_el.get_text(" ", strip=True) if body_el else post_el.get_text(" ", strip=True)
            if not text:
                continue

            posts.append({
                "url": thread_url,
                "thread_title": thread_title,
                "author": author_el.get_text(strip=True) if author_el else "",
                "posted_at": date_el.get("datetime", "") if date_el else "",
                "text": text[:4000],
                "forum": "mumsnet",
            })
            if len(posts) >= MAX_POSTS_PER_THREAD:
                break
        return posts


class TheStudentRoomParser:
    """
    Crawls The Student Room threads.
    Expects the source URL to be a forum/search page, e.g.:
      https://www.thestudentroom.co.uk/forumdisplay.php?f=33
    """

    DOMAIN = "thestudentroom.co.uk"

    def thread_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        for a in soup.select("a.threadbit__title-link, a[href*='showthread']"):
            href = a.get("href", "")
            full = urljoin(base_url, href).split("&page")[0]
            if full not in links:
                links.append(full)
        return links[:MAX_THREADS_PER_SOURCE]

    def parse_thread(self, soup: BeautifulSoup, thread_url: str) -> list[dict]:
        posts = []
        title_el = soup.select_one("h1.thread-title, h1")
        thread_title = title_el.get_text(strip=True) if title_el else ""

        for post_el in soup.select(".post__content, .postbit"):
            author_el = post_el.select_one(".post__user-name, .username")
            date_el = post_el.select_one("time, .post__timestamp")
            body_el = post_el.select_one(".post__body, .postcontent")

            text = body_el.get_text(" ", strip=True) if body_el else post_el.get_text(" ", strip=True)
            if not text:
                continue

            posts.append({
                "url": thread_url,
                "thread_title": thread_title,
                "author": author_el.get_text(strip=True) if author_el else "",
                "posted_at": date_el.get("datetime", date_el.get_text(strip=True)) if date_el else "",
                "text": text[:4000],
                "forum": "thestudentroom",
            })
            if len(posts) >= MAX_POSTS_PER_THREAD:
                break
        return posts


class NetmumsParser:
    """
    Crawls Netmums forum threads.
    Expects the source URL to be a category or search page.
    """

    DOMAIN = "netmums.com"

    def thread_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        links = []
        for a in soup.select("a[href]"):
            href = a["href"]
            if "/coffeehouse/" in href or "/back-to-school/" in href:
                full = urljoin(base_url, href).split("?")[0]
                if full not in links and full != base_url:
                    links.append(full)
        return links[:MAX_THREADS_PER_SOURCE]

    def parse_thread(self, soup: BeautifulSoup, thread_url: str) -> list[dict]:
        posts = []
        title_el = soup.select_one("h1")
        thread_title = title_el.get_text(strip=True) if title_el else ""

        for post_el in soup.select(".post, article.comment"):
            author_el = post_el.select_one(".author, .username")
            date_el = post_el.select_one("time, .date")
            body_el = post_el.select_one(".post-content, .message-body, p")

            text = body_el.get_text(" ", strip=True) if body_el else post_el.get_text(" ", strip=True)
            if not text:
                continue

            posts.append({
                "url": thread_url,
                "thread_title": thread_title,
                "author": author_el.get_text(strip=True) if author_el else "",
                "posted_at": date_el.get("datetime", date_el.get_text(strip=True)) if date_el else "",
                "text": text[:4000],
                "forum": "netmums",
            })
            if len(posts) >= MAX_POSTS_PER_THREAD:
                break
        return posts


class GenericForumParser:
    """Fallback parser — stores each page's full visible text as one document."""

    DOMAIN = None

    def thread_links(self, soup: BeautifulSoup, base_url: str) -> list[str]:
        return []

    def parse_thread(self, soup: BeautifulSoup, thread_url: str) -> list[dict]:
        text = soup.get_text(" ", strip=True)[:8000]
        return [{"url": thread_url, "thread_title": "", "author": "", "posted_at": "", "text": text, "forum": "generic"}]


PARSERS = [MumsnetParser(), TheStudentRoomParser(), NetmumsParser()]


def get_parser(url: str):
    domain = urlparse(url).netloc.lower()
    for parser in PARSERS:
        if parser.DOMAIN and parser.DOMAIN in domain:
            return parser
    return GenericForumParser()


# ---------------------------------------------------------------------------
# Crawler core
# ---------------------------------------------------------------------------


def crawl_source(conn, source: dict, dry_run: bool, client: httpx.Client) -> dict:
    url = source["url"]
    source_id = str(source["id"])
    log.info("Crawling source: %s  (%s)", source["source_name"], url)

    parser = get_parser(url)
    log.info("Using parser: %s", type(parser).__name__)

    stats = {"threads": 0, "posts": 0, "new_docs": 0, "skipped": 0, "errors": 0}

    # Fetch index / search page
    soup = fetch(client, url)
    if soup is None:
        log.error("Could not fetch source URL: %s", url)
        stats["errors"] += 1
        return stats

    thread_links = parser.thread_links(soup, url)

    # If this is already a thread page (direct link), treat it as one thread
    if not thread_links:
        log.info("No thread links found — treating source URL as a thread page.")
        thread_links = [url]

    log.info("Found %d thread(s) to crawl.", len(thread_links))

    for thread_url in thread_links:
        stats["threads"] += 1
        time.sleep(RATE_LIMIT_SECONDS)

        thread_soup = fetch(client, thread_url)
        if thread_soup is None:
            stats["errors"] += 1
            continue

        posts = parser.parse_thread(thread_soup, thread_url)
        log.info("  Thread: %s  → %d post(s)", thread_url[:80], len(posts))

        for post in posts:
            stats["posts"] += 1
            if not post["text"].strip():
                stats["skipped"] += 1
                continue

            meta = {
                "url": post["url"],
                "thread_title": post["thread_title"],
                "author": post["author"],
                "posted_at": post["posted_at"],
                "forum": post["forum"],
                "school_id": str(source["school_id"]) if source["school_id"] else None,
                "source_name": source["source_name"],
            }

            if dry_run:
                log.info("    [DRY RUN] Would insert: %s ...", post["text"][:80])
                stats["new_docs"] += 1
            else:
                try:
                    inserted = insert_document(conn, source_id, "post", post["text"], meta)
                    if inserted:
                        stats["new_docs"] += 1
                    else:
                        stats["skipped"] += 1
                except Exception as e:
                    log.warning("    DB insert failed: %s", e)
                    conn.rollback()
                    stats["errors"] += 1

        if not dry_run:
            conn.commit()

    return stats


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="School Signal forum crawler")
    parser.add_argument("--source-id", help="Crawl a single source by UUID")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to the database")
    parser.add_argument("--verbose", action="store_true", help="Debug logging")
    args = parser.parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    conn = get_db_connection()
    sources = load_forum_sources(conn, source_id=args.source_id)

    if not sources:
        log.warning(
            "No active forum sources found. "
            "Add rows to the `sources` table with access_method='webscrape', "
            "or check the --source-id argument."
        )
        return

    log.info("Loaded %d source(s).", len(sources))

    totals = {"threads": 0, "posts": 0, "new_docs": 0, "skipped": 0, "errors": 0}

    with httpx.Client(follow_redirects=True, timeout=REQUEST_TIMEOUT) as client:
        for source in sources:
            stats = crawl_source(conn, source, dry_run=args.dry_run, client=client)
            for k in totals:
                totals[k] += stats[k]
            time.sleep(RATE_LIMIT_SECONDS * 2)  # between sources

    conn.close()

    log.info(
        "Done.  threads=%d  posts=%d  new_docs=%d  skipped=%d  errors=%d",
        totals["threads"], totals["posts"], totals["new_docs"],
        totals["skipped"], totals["errors"],
    )


if __name__ == "__main__":
    main()
