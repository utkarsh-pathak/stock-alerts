from decimal import Decimal
import logging
import requests

from django.db.models import QuerySet

from stocks.models import (
    CREATED,
    TRIGGERED,
    Stocks, 
    User
)

logger = logging.getLogger(__name__)
DEFAULT_STOCKS_FETCH_URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'


def feed_stocks():
    try:
        response = requests.get(DEFAULT_STOCKS_FETCH_URL)
        if not response.ok:
            raise Exception('Error while fetching stocks info. Double check the URL passed !')
        for each in response.json():
            # Perform `Upsert` operation
            current_price = Decimal(each['current_price'])
            obj, created = Stocks.objects.update_or_create(
                name=each['name'],
                stock_id=each['id'],
                symbol=each['symbol'],
                defaults={'current_price':current_price}
                )
            if not created:
                # Means that we may have alerts in place for an existing stock.
                qs = obj.alerts.filter(desired_price=current_price, status=CREATED)
                if qs.exists(): # Means that we have found alerts which should be triggered.
                    try:
                        handle_alerts(qs)
                    except Exception:
                        print('Retry logic should be in place here.')
                    else:
                        qs.update(status=TRIGGERED)

    except Exception as e:
        logger.exception(f'Exception - {str(e)}', exc_info=True)


def handle_alerts(qs: QuerySet):
    """ As of now, this function will not do anything.
        It will only print to the console.
    """
    for obj in qs:
        send_email(obj.user, obj.stock, obj.desired_price)


def send_email(user: User, stock: Stocks, desired_price: Decimal):
    print(
        f'Dear {user.username}\n'
        f'Your alert on the stock {stock.name} with the desired price {desired_price} has been triggered.'
    )