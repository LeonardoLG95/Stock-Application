from django.shortcuts import render
from django.views import generic

from .models import StockData


class StockListView(generic.ListView):
    model = StockData

    def get_queryset(self):
        return StockData.objects.filter().distinct('ticker')
