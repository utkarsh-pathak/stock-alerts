import os


from django.conf import settings
from celery import Celery


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "stock_alerts.settings")
app = Celery("stock_alerts")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


if __name__ == '__main__':
    app.start()
