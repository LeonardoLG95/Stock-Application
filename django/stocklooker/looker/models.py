from django.db import models
from datetime import datetime


class StockData(models.Model):
    id = models.CharField(max_length=50, help_text="Id mix of date-ticker", primary_key=True)
    insert_date = models.DateTimeField(help_text="Registration date", default=datetime.now(), blank=True)
    date = models.DateTimeField(help_text="Data date")
    yahoo_ticker = models.CharField(max_length=10, help_text="Ticker for easy search the stock")
    open = models.FloatField(help_text="Value of the stock at the start of the day")
    close = models.FloatField(help_text="Value of the stock at the end of the day")
    low = models.FloatField(help_text="Low value on the day")
    high = models.FloatField(help_text="High value on the day")
    volume = models.IntegerField(help_text="Volume of transactions this day")
    macd_12_26 = models.FloatField(help_text="Macd value on that day")
    signal_12_26 = models.FloatField(help_text="Signal value on that day")
    rsi_14 = models.FloatField(help_text="Rsi value on that day")

    def __str__(self):
        return self.field_name


class Names(models.Model):
    yahoo_ticker = models.CharField(max_length=10, help_text="Ticker for easy search the stock", primary_key=True)
    name = models.CharField(max_length=50, help_text="Name of the bussiness")

    def __str__(self):
        return self.field_name
