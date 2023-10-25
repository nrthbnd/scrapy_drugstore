import scrapy
from datetime import datetime
from scrapy.http import Request

from scrapy_drugstore.items import ScrapyDrugstoreItem


class MaksavitSpider(scrapy.Spider):
    name = "maksavit"
    allowed_domains = ["maksavit.ru"]
    # start_urls = ["http://maksavit.ru/catalog/materinstvo_i_detstvo/"]
    start_urls = ["https://maksavit.ru/novosibirsk/catalog/materinstvo_i_detstvo/detskaya_gigiena/"]

    def parse(self, response):
        """Загрузить со страницы категории данные о представленных товарах."""
        main_section = response.css('span.breadcrumbs__link::text').get().strip()

        products = response.css('div.grid-type-container')
        for product in products.css('div.product-card-block'):
            card_block = product.css('a.product-card-block__title')
            short_url = card_block.css('::attr(href)').get()

            timestamp = datetime.timestamp(datetime.now())
            item_id = short_url.split('/')[-2]
            url = Request(response.urljoin(short_url)).url
            title = card_block.css('span::text').get()
            marketing_tags = product.css('div.badge-discount::text').get().strip()
            category = product.css('a.product-card-block__category::text').get().strip()
            data = {
                'timestamp': timestamp,
                'RPC': item_id,
                'url': url,
                'title': title,
                'marketing_tags': marketing_tags,
                'section': [main_section, category]
            }
            yield ScrapyDrugstoreItem(data)
