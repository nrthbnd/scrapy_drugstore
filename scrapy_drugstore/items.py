import scrapy


class ScrapyDrugstoreItem(scrapy.Item):
    """Определить данные, извлекаемые при парсинге."""
    timestamp = scrapy.Field()
    RPC = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    marketing_tags = scrapy.Field()
    brand = scrapy.Field()
    section = scrapy.Field()
