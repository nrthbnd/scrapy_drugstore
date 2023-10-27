

def calculate_sale(current_price: str, original_price: str) -> str:
    """Вычислить процент скидки."""
    if current_price != original_price:
        sale_amount = round(
            100 - 100 * int(current_price) / int(original_price),
            2,
        )
        sale = f'Скидка {sale_amount}%.'
    else:
        sale = ''
    return sale
