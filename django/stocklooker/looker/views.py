import asyncio

from django.shortcuts import render

from .models import StockData

def index(request):
    return render(
        request,
        'index.html'
    )


def stock_list(request):
    return render(
        request,
        'stock_list.html',
        context={}
    )


def update(request):
    stock_data = StockData

    async def main():
        markets = ['DOW JONES', 'S&P 500', 'NASDAQ 100']
        driver = YahooDriver(markets=markets)
        await driver.return_stocks()

    asyncio.run(main)

    return render(
        request,
        'update.html'
    )
