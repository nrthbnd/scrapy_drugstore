import os
import re
import scrapy
from datetime import datetime
from scrapy.http import Request

from scrapy_drugstore.items import ScrapyDrugstoreItem


class MaksavitSpider(scrapy.Spider):
    name = 'maksavit'
    domain = os.getenv('ALLOWED_DOMAIN', '')
    urls = os.getenv('START_URL', '').split(',')
    for url in urls:
        if 'novosibirsk' not in url:
            url = url.replace(domain, domain + '/novosibirsk/')

    allowed_domains = [domain]
    start_urls = urls

    def parse(self, response):
        """Загрузить со страницы категории общие данные
        о каждом из представленных товаров."""
        breadcrumbs = response.css('ul.breadcrumbs')
        breadcrumbs_li = breadcrumbs.css('li:nth-child(3)')
        main_section = breadcrumbs_li.css('span::text').get().strip()

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

            yield response.follow(
                url,
                callback=self.parse_product,
                cb_kwargs={'data': data},
            )

        # Пагинация:
        pagination_ul = response.css('ul.ui-pagination')
        last_page = pagination_ul.css('li:nth-last-child(2)')
        last_page_href = last_page.css('a::attr(href)').get().split('/?page=')
        short_link, last_page_num1 = last_page_href[0], last_page_href[-1]

        for page in range(2, int(last_page_num1) + 1):
            page_link = response.urljoin(
                short_link + '/?page=' + str(page))
            yield response.follow(page_link, callback=self.parse)

    def parse_product(self, response, data):
        """Загрузить со страницы товара специфичные данные о нем."""
        brand_country_info = response.css('a.product-info__brand-value::text')
        if not brand_country_info:
            brand, country = '', ''
        else:
            brand_country_parts = brand_country_info.get().strip().split(',')
            brand = brand_country_parts[0].strip()
            country = brand_country_parts[2].strip() if len(
                brand_country_parts) > 2 else ''

        price_box = response.css('div.price-box')
        current_price = price_box.css('span.price-value::text').get()
        current_price = re.sub(r'[^\d.]', '', current_price)
        original_price = price_box.css('div.price-box__old-price::text').get()
        if not original_price:
            original_price = current_price
        else:
            original_price = re.sub(r'[^\d.]', '', original_price)

        if current_price != original_price:
            sale_amount = round(
                100 - 100 * int(current_price) / int(original_price), 2)
            sale = f'Скидка {sale_amount}%.'
        else:
            sale = ''

        price_box_controls = price_box.css('div.price-box__controls')
        button = price_box_controls.css('button.button::text').get()
        if button.strip() == 'В корзину':
            in_stock = True
        else:
            in_stock = False

        product_picture = response.css('div.product-picture')
        main_image_src = product_picture.css('img::attr(src)').get()
        if not main_image_src:
            main_image = ''
        else:
            main_image = response.urljoin(main_image_src)

        product_instruction = response.css('div.product-instruction__guide')
        metadata = {}
        if country != '':
            metadata['Страна производитель'] = country
        for item in product_instruction.css('div'):
            name_item = item.css('h3::text')
            if name_item:
                name = name_item.get()
                description_parts = item.xpath('.//text()').getall()
                description = ' '.join(description_parts).strip()
                if description:
                    description = re.sub(
                        r'^\s*' + re.escape(name) + r'\s*', '', description)
                    description = re.sub(r'\s+', ' ', description)
                    metadata[name] = description.strip()

        specific_data = {
                'brand': brand,
                'price_data': {
                    'current': current_price,
                    'original': original_price,
                    'sale_tag': sale,
                },
                'stock': {
                    'in_stock': in_stock,
                    'count': 0,
                },
                'assets': {
                    'main_image': main_image,
                    'set_images': [''],
                    'view360': [''],
                    'video': '',
                },
                'metadata': metadata,
                'variants': 0,
        }
        data.update(specific_data)
        yield ScrapyDrugstoreItem(data)
