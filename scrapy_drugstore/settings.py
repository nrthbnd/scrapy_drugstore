from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).parent

BOT_NAME = "scrapy_drugstore"

SPIDER_MODULES = ["scrapy_drugstore.spiders"]
NEWSPIDER_MODULE = "scrapy_drugstore.spiders"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

DEFAULT_REQUEST_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:32.0) Gecko/20100101 Firefox/32.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
}

ITEM_PIPELINES = {
   "scrapy_drugstore.pipelines.ScrapyDrugstorePipeline": 300,
}

REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"

# Параметры сохранения полученных данных:
FEEDS = {
    (BASE_DIR / 'results/scrapy_result.json').as_posix(): {
        'format': 'json',
        'fields': [
            'timestamp', 'RPC', 'url', 'title', 'marketing_tags', 'brand',
            'section', 'price_data', 'stock', 'assets', 'metadata', 'variants'
        ],
        'overwrite': True,
    }
}
