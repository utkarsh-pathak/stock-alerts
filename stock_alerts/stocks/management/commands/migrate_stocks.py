from datetime import timedelta
from decimal import Decimal
import logging

import requests
from stocks.models import Stocks

from django.core.management.base import BaseCommand, CommandError
from django.utils.timezone import now


logger = logging.getLogger(__name__)

DEFAULT_STOCKS_FETCH_URL = 'https://api.coingecko.com/api/v3/coins/markets?vs_currency=USD&order=market_cap_desc&per_page=100&page=1&sparkline=false'

class Command(BaseCommand):
    help = "Populates the database with stocks"  # noqa A003

    def add_arguments(self, parser):
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            default=DEFAULT_STOCKS_FETCH_URL,
            help="URL to fetch stocks information",
        )
        

    def handle(self, **options):
        url = options.get('url')
        
        # Fetch and populate the database with the stock info

        try:
            response = requests.get(url)
            if not response.ok:
                raise Exception('Error while fetching stocks info. Double check the URL passed !')
            for each in response.json():
                # Perform `Upsert` operation
                obj, _ = Stocks.objects.update_or_create(
                    name=each['name'],
                    stock_id=each['id'],
                    symbol=each['symbol'],
                    defaults={'current_price':Decimal(each['current_price'])}
                    )
        except Exception as e:
            logger.exception(f'Exception - {str(e)}', exc_info=True)
        