EMPTY_STR = ''
WHITESPACE_STR = ' '
PAGE_URL = '/?page='

# html_tags parse
BREADCRUMBS_TAG = 'ul.breadcrumbs'
BREADCRUMBS_LI_TAG = 'li:nth-child(3)'
MAIN_SECTION_TAG = 'span::text'
PRODUCTS = 'div.grid-type-container'
PRODUCT_CARD_BLOCK = 'div.product-card-block'
CARD_BLOCK_TITLE = 'a.product-card-block__title'
SHORT_URL = '::attr(href)'
TITLE_TEXT = 'span::text'
CATEGORY_TEXT = 'a.product-card-block__category::text'
BADGE_DISCOUNT = 'div.badge-discount'
TEXT_TAG = '::text'

# html_tags parse_product
PRODUCT_INFO_TAG = 'a.product-info__brand-value::text'
PRICE_BOX_TAG = 'div.price-box'
CURRENT_PRICE_TAG = 'span.price-value::text'
ORIGINAL_PRICE_TAG = 'div.price-box__old-price::text'
PRICE_BOX_CONTROLS_TAG = 'div.price-box__controls'
BUTTON_TEXT_TAG = 'button.button::text'
BUTTON_TEXT = 'В корзину'
PRODUCT_PICTURE_TAG = 'div.product-picture'
MAIN_IMAGE_TAG = 'img::attr(src)'
PRODUCT_INSTRUCTION_TAG = 'div.product-instruction__guide'
COUNTRY_META = 'Страна производитель'
DIV_TAG = 'div'
DESCRIPTION_TITLE_TAG = 'h3::text'
DESCRIPTION_TEXT_TAG = './/text()'

# pagination_tags
PAGINATION_UL_TAG = 'ul.ui-pagination'
LAST_PAGE_TAG = 'li:nth-last-child(2)'
LAST_PAGE_HREF = 'a::attr(href)'

# search_region
CITY = 'novosibirsk'

# regular_expressions
# выюрать символы, которые не являются цифрой или точкой
ALL_EXCEPT_DIGITS_AND_PERIOD = r'[^\d.]'
# выбрать все пробелы в начале строки
WHITESPACES_ZERO_PLUS_BEG = r'^\s*'
# выбрать все пробелы
WHITESPACES_ZERO_PLUS = r'\s*'
# выбрать одно или более повторений пробела
WHITESPACES_ONE_PLUS = r'\s+'
