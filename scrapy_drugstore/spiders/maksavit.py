import os
import re
from datetime import datetime
from typing import Dict

import scrapy
from scrapy_drugstore.constants import (
    ALL_EXCEPT_DIGITS_AND_PERIOD,
    BADGE_DISCOUNT, BREADCRUMBS_LI_TAG,
    BREADCRUMBS_TAG, BUTTON_TEXT,
    BUTTON_TEXT_TAG, CARD_BLOCK_TITLE,
    CATEGORY_TEXT, CITY,
    COUNTRY_META, CURRENT_PRICE_TAG,
    DESCRIPTION_TEXT_TAG, SPAN_TEXT,
    DESCRIPTION_TITLE_TAG, DIV_TAG,
    EMPTY_STR, LAST_PAGE_HREF,
    LAST_PAGE_TAG, MAIN_IMAGE_TAG,
    ORIGINAL_PRICE_TAG,
    PAGE_URL, PAGINATION_UL_TAG,
    PRICE_BOX_CONTROLS_TAG, PRICE_BOX_TAG,
    PRODUCT_CARD_BLOCK, PRODUCT_INFO_TAG,
    PRODUCT_INSTRUCTION_TAG,
    PRODUCT_PICTURE_TAG, PRODUCTS,
    SHORT_URL, TEXT_TAG,
    WHITESPACE_STR, WHITESPACES_ONE_PLUS,
    WHITESPACES_ZERO_PLUS,
    WHITESPACES_ZERO_PLUS_BEG)
from scrapy_drugstore.items import ScrapyDrugstoreItem
from scrapy_drugstore.utils import calculate_sale


class MaksavitSpider(scrapy.Spider):
    name = 'maksavit'
    domain = os.getenv('ALLOWED_DOMAIN', EMPTY_STR)
    urls = os.getenv('START_URL', EMPTY_STR).split(',')
    for url in urls:
        if CITY not in url:
            url = url.replace(domain, domain + '/' + CITY + '/')

    allowed_domains = [domain]
    start_urls = urls

    def parse(self, response: scrapy.http.Response) -> Dict[str, str]:
        """Загрузить со страницы категории общие данные
        о каждом из представленных товаров."""
        breadcrumbs = response.css(BREADCRUMBS_TAG)
        breadcrumbs_li = breadcrumbs.css(BREADCRUMBS_LI_TAG)
        main_section = breadcrumbs_li.css(SPAN_TEXT).get().strip()

        products = response.css(PRODUCTS)
        for product in products.css(PRODUCT_CARD_BLOCK):
            card_block = product.css(CARD_BLOCK_TITLE)
            short_url = card_block.css(SHORT_URL).get()

            timestamp = datetime.timestamp(datetime.now())
            item_id = short_url.split('/')[-2]
            url = response.urljoin(short_url)
            title = card_block.css(SPAN_TEXT).get()
            category = product.css(
                CATEGORY_TEXT).get().strip()

            marketing_full = product.css(BADGE_DISCOUNT)
            marketing_tags = ([] if not marketing_full else (
                marketing_full.css(TEXT_TAG).get().strip()))

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

        pagination_ul = response.css(PAGINATION_UL_TAG)
        last_page = pagination_ul.css(LAST_PAGE_TAG)
        last_page_href = last_page.css(LAST_PAGE_HREF).get().split(PAGE_URL)
        short_link, last_page_num1 = last_page_href[0], last_page_href[-1]

        for page in range(2, int(last_page_num1) + 1):
            page_link = response.urljoin(
                short_link + PAGE_URL + str(page))
            yield response.follow(page_link, callback=self.parse)

    def parse_product(
            self,
            response: scrapy.http.Response,
            data: Dict
    ) -> Dict[str, str]:
        """Загрузить со страницы товара специфичные данные о нем."""
        brand_country_info = response.css(PRODUCT_INFO_TAG)
        if not brand_country_info:
            brand, country = EMPTY_STR, EMPTY_STR
        else:
            brand_country_parts = brand_country_info.get().strip().split(',')
            brand = brand_country_parts[0].strip()
            country = brand_country_parts[2].strip() if len(
                brand_country_parts) > 2 else EMPTY_STR

        price_box = response.css(PRICE_BOX_TAG)
        current_price = price_box.css(CURRENT_PRICE_TAG).get()
        current_price = re.sub(
            ALL_EXCEPT_DIGITS_AND_PERIOD, EMPTY_STR, current_price)
        original_price = price_box.css(ORIGINAL_PRICE_TAG).get()
        original_price = current_price if not original_price else (
            re.sub(ALL_EXCEPT_DIGITS_AND_PERIOD, EMPTY_STR, original_price))
        sale = calculate_sale(current_price, original_price)

        price_box_controls = price_box.css(PRICE_BOX_CONTROLS_TAG)
        button = price_box_controls.css(BUTTON_TEXT_TAG).get()
        in_stock = True if button.strip() == BUTTON_TEXT else False

        product_picture = response.css(PRODUCT_PICTURE_TAG)
        main_image_src = product_picture.css(MAIN_IMAGE_TAG).get()
        main_image = EMPTY_STR if not main_image_src else (
            response.urljoin(main_image_src))

        product_instruction = response.css(PRODUCT_INSTRUCTION_TAG)
        metadata = {}
        if country != EMPTY_STR:
            metadata[COUNTRY_META] = country
        for item in product_instruction.css(DIV_TAG):
            name_item = item.css(DESCRIPTION_TITLE_TAG)
            if name_item:
                name = name_item.get()
                description_parts = item.xpath(DESCRIPTION_TEXT_TAG).getall()
                description = WHITESPACE_STR.join(description_parts).strip()
                if description:
                    description = re.sub(
                        WHITESPACES_ZERO_PLUS_BEG + re.escape(name) + (
                            WHITESPACES_ZERO_PLUS),
                        EMPTY_STR,
                        description)
                    description = re.sub(
                        WHITESPACES_ONE_PLUS, WHITESPACE_STR, description)
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
                    'set_images': [EMPTY_STR],
                    'view360': [EMPTY_STR],
                    'video': EMPTY_STR,
                },
                'metadata': metadata,
                'variants': 0,
        }
        data.update(specific_data)
        yield ScrapyDrugstoreItem(data)
