"""Append India/Kerala/Government_India source sections to sources.yaml."""
import pathlib

SOURCES_YAML = pathlib.Path(__file__).parent.parent / "app" / "pipeline" / "config" / "sources.yaml"

INDIA_KERALA_SOURCES = """
# ---------------------------------------------------------------------------
# INDIA - National News (PRIMARY)
# ---------------------------------------------------------------------------
india:
  - name: "The Hindu"
    url: "https://www.thehindu.com"
    domain: "thehindu.com"
    feed_url: "https://www.thehindu.com/feeder/default.rss"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: high
    reliability_score: 0.95
    fetch_interval_minutes: 5
    active: true

  - name: "NDTV"
    url: "https://www.ndtv.com"
    domain: "ndtv.com"
    feed_url: "https://feeds.feedburner.com/ndtvnews-top-stories"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: high
    reliability_score: 0.90
    fetch_interval_minutes: 5
    active: true

  - name: "Times of India"
    url: "https://timesofindia.indiatimes.com"
    domain: "timesofindia.indiatimes.com"
    feed_url: "https://timesofindia.indiatimes.com/rssfeedstopstories.cms"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: high
    reliability_score: 0.85
    fetch_interval_minutes: 5
    active: true

  - name: "Indian Express"
    url: "https://indianexpress.com"
    domain: "indianexpress.com"
    feed_url: "https://indianexpress.com/feed/"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.90
    fetch_interval_minutes: 10
    active: true

  - name: "Hindustan Times"
    url: "https://www.hindustantimes.com"
    domain: "hindustantimes.com"
    feed_url: "https://www.hindustantimes.com/feeds/rss/topnews/rssfeed.xml"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "India Today"
    url: "https://www.indiatoday.in"
    domain: "indiatoday.in"
    feed_url: "https://www.indiatoday.in/rss/home"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "News18 India"
    url: "https://www.news18.com"
    domain: "news18.com"
    feed_url: "https://www.news18.com/commonfeeds/v1/eng/rss/india.xml"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.80
    fetch_interval_minutes: 10
    active: true

  - name: "The Wire"
    url: "https://thewire.in"
    domain: "thewire.in"
    feed_url: "https://thewire.in/feed"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "Scroll.in"
    url: "https://scroll.in"
    domain: "scroll.in"
    feed_url: "https://scroll.in/feed"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "The Print"
    url: "https://theprint.in"
    domain: "theprint.in"
    feed_url: "https://theprint.in/feed/"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "Live Mint"
    url: "https://www.livemint.com"
    domain: "livemint.com"
    feed_url: "https://www.livemint.com/rss/homepage"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.88
    fetch_interval_minutes: 10
    active: true

  - name: "Economic Times"
    url: "https://economictimes.indiatimes.com"
    domain: "economictimes.indiatimes.com"
    feed_url: "https://economictimes.indiatimes.com/rssfeedstopstories.cms"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.88
    fetch_interval_minutes: 10
    active: true

  - name: "Business Standard"
    url: "https://www.business-standard.com"
    domain: "business-standard.com"
    feed_url: "https://www.business-standard.com/rss/home_page_top_stories.rss"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.88
    fetch_interval_minutes: 10
    active: true

  - name: "The New Indian Express"
    url: "https://www.newindianexpress.com"
    domain: "newindianexpress.com"
    feed_url: "https://www.newindianexpress.com/rss/news.xml"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.82
    fetch_interval_minutes: 10
    active: true

  - name: "Deccan Chronicle"
    url: "https://www.deccanchronicle.com"
    domain: "deccanchronicle.com"
    feed_url: "https://www.deccanchronicle.com/rss-feeds/"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.80
    fetch_interval_minutes: 15
    active: true

# ---------------------------------------------------------------------------
# KERALA - Regional News (PRIMARY)
# ---------------------------------------------------------------------------
kerala:
  - name: "Mathrubhumi English"
    url: "https://english.mathrubhumi.com"
    domain: "english.mathrubhumi.com"
    feed_url: "https://english.mathrubhumi.com/rss/news"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: high
    reliability_score: 0.90
    fetch_interval_minutes: 3
    active: true

  - name: "Manorama Online English"
    url: "https://english.manoramaonline.com"
    domain: "english.manoramaonline.com"
    feed_url: "https://english.manoramaonline.com/rss/news.xml"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: high
    reliability_score: 0.90
    fetch_interval_minutes: 3
    active: true

  - name: "The Hindu - Kerala"
    url: "https://www.thehindu.com"
    domain: "thehindu.com"
    feed_url: "https://www.thehindu.com/news/states/kerala/feeder/default.rss"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: high
    reliability_score: 0.95
    fetch_interval_minutes: 5
    active: true

  - name: "NDTV - Kerala"
    url: "https://www.ndtv.com"
    domain: "ndtv.com"
    feed_url: "https://feeds.feedburner.com/ndtvnews-kerala"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: high
    reliability_score: 0.90
    fetch_interval_minutes: 5
    active: true

  - name: "Times of India - Kerala"
    url: "https://timesofindia.indiatimes.com"
    domain: "timesofindia.indiatimes.com"
    feed_url: "https://timesofindia.indiatimes.com/rssfeeds/-2128936541.cms"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "The New Indian Express - Kerala"
    url: "https://www.newindianexpress.com"
    domain: "newindianexpress.com"
    feed_url: "https://www.newindianexpress.com/rss/states/kerala.xml"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "Onmanorama"
    url: "https://www.onmanorama.com"
    domain: "onmanorama.com"
    feed_url: "https://www.onmanorama.com/rss"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: normal
    reliability_score: 0.82
    fetch_interval_minutes: 10
    active: true

  - name: "India Today - Kerala"
    url: "https://www.indiatoday.in"
    domain: "indiatoday.in"
    feed_url: "https://www.indiatoday.in/rss/1206614"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: normal
    reliability_score: 0.85
    fetch_interval_minutes: 10
    active: true

  - name: "Asianet News"
    url: "https://newsable.asianetnews.com"
    domain: "newsable.asianetnews.com"
    feed_url: "https://newsable.asianetnews.com/rss"
    source_type: rss
    language: en
    country: in
    region: KERALA
    priority: normal
    reliability_score: 0.80
    fetch_interval_minutes: 10
    active: true

# ---------------------------------------------------------------------------
# GOVERNMENT_INDIA - Official Government and Institutional Sources
# ---------------------------------------------------------------------------
government_india:
  - name: "PIB India"
    url: "https://pib.gov.in"
    domain: "pib.gov.in"
    feed_url: "https://pib.gov.in/RssMain.aspx"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: high
    reliability_score: 0.98
    fetch_interval_minutes: 5
    active: true

  - name: "Reserve Bank of India"
    url: "https://www.rbi.org.in"
    domain: "rbi.org.in"
    feed_url: "https://www.rbi.org.in/Scripts/RSS.aspx?Id=316"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.99
    fetch_interval_minutes: 30
    active: true

  - name: "India Meteorological Department"
    url: "https://mausam.imd.gov.in"
    domain: "mausam.imd.gov.in"
    feed_url: "https://mausam.imd.gov.in/rss.php"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: high
    reliability_score: 0.99
    fetch_interval_minutes: 5
    active: true

  - name: "Ministry of External Affairs India"
    url: "https://www.mea.gov.in"
    domain: "mea.gov.in"
    feed_url: "https://www.mea.gov.in/index.htm?rss=yes"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.98
    fetch_interval_minutes: 15
    active: true

  - name: "SEBI"
    url: "https://www.sebi.gov.in"
    domain: "sebi.gov.in"
    feed_url: "https://www.sebi.gov.in/sebiweb/other/OtherAction.do?doRss=yes"
    source_type: rss
    language: en
    country: in
    region: INDIA
    priority: normal
    reliability_score: 0.99
    fetch_interval_minutes: 30
    active: true
"""

if __name__ == "__main__":
    existing = SOURCES_YAML.read_text(encoding="utf-8")
    # Guard: only append if sections not already present
    if "# INDIA - National News" in existing:
        print("India/Kerala sections already present – skipping.")
    else:
        with open(SOURCES_YAML, "a", encoding="utf-8") as f:
            f.write(INDIA_KERALA_SOURCES)
        print(f"Appended India/Kerala/Government sources to {SOURCES_YAML}")

    # Validate YAML parses correctly
    import yaml
    with open(SOURCES_YAML, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    india_count = len(data.get("india", []))
    kerala_count = len(data.get("kerala", []))
    govt_count = len(data.get("government_india", []))
    print(f"Validation OK: india={india_count}, kerala={kerala_count}, government_india={govt_count}")
