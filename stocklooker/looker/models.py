from django.db import models
from datetime import datetime

class StockData(models.Model):
    # Fields
    insert_date = models.DateTimeField(help_text="Registration date", default=datetime.now, blank=True)
    date = models.DateTimeField(help_text="Data date")
    ticker = models.CharField(max_length=10, help_text="Ticker for easy search the stock")
    name = models.CharField(max_length=50, help_text="Name of the bussiness", blank=True)
    market = models.CharField(max_length=50, help_text="Name of the market, options for now: SP500, Nasdaq and Dow", blank=True)
    value = models.FloatField(help_text="Value of the stock this day")
    low = models.FloatField(help_text="Low value on the day")
    high = models.FloatField(help_text="High value on the day")
    macd = models.FloatField(help_text="Macd value on that day")
    signal = models.FloatField(help_text="Signal value on that day")
    rsi = models.FloatField(help_text="Rsi value on that day")

    # Metadata
    class Meta:
        ordering = ["ticker"]


    '''
    # Métodos
    def get_absolute_url(self):
         """
         Devuelve la url para acceder a una instancia particular de MyModelName.
         """
         return reverse('model-detail-view', args=[str(self.id)])
    '''
    def __str__(self):
        """
        Cadena para representar el objeto MyModelName (en el sitio de Admin, etc.)
        """
        return self.field_name
