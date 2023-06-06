import logging

from celery import shared_task
from stocks.models import *
from stocks.biz_utils import feed_stocks

logger = logging.getLogger(__name__)


@shared_task(queue='handle_stock_alerts')
def handle_stock_alerts():
    feed_stocks()