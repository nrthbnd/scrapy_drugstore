import scrapy
from datetime import datetime
from scrapy.http import Request

from scrapy_drugstore.items import ScrapyDrugstoreItem


class MaksavitSpider(scrapy.Spider):
    name = 'maksavit'
    allowed_domains = ["maksavit.ru"]
    start_urls = ["https://maksavit.ru/novosibirsk/catalog/materinstvo_i_detstvo/detskaya_gigiena/"]

    def parse(self, response):
        """Загрузить со страницы категории данные о представленных товарах."""
        main_section = response.css(
            'span.breadcrumbs__link::text').get().strip()

        products = response.css('div.grid-type-container')
        for product in products.css('div.product-card-block'):
            card_block = product.css('a.product-card-block__title')
            short_url = card_block.css('::attr(href)').get()

            timestamp = datetime.timestamp(datetime.now())
            item_id = short_url.split('/')[-2]
            url = Request(response.urljoin(short_url)).url
            title = card_block.css('span::text').get()
            category = product.css(
                'a.product-card-block__category::text').get().strip()

            marketing_full = product.css('div.badge-discount')
            if not marketing_full:
                marketing_tags = []
            else:
                marketing_tags = marketing_full.css('::text').get().strip()

            data = {
                'timestamp': timestamp,
                'RPC': item_id,
                'url': url,
                'title': title,
                'marketing_tags': marketing_tags,
                'section': [main_section, category]
            }
            yield ScrapyDrugstoreItem(data)

        pagination_ul = response.css('ul.ui-pagination')
        last_page = pagination_ul.css('li:nth-last-child(2)')
        last_page_href = last_page.css('a::attr(href)').get().split('/?page=')
        short_link, last_page_num1 = last_page_href[0], last_page_href[-1]

        for page in range(2, int(last_page_num1) + 1):
            page_link = response.urljoin(
                short_link + '/?page=' + str(page))
            yield response.follow(page_link, callback=self.parse)
