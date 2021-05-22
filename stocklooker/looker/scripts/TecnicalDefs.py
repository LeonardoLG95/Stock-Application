import random

def calcRsi(prices):
    prices = prices[-14:]
    i = 1
    avgUp = 0
    avgDown = 0

    while i < 14:
        difference = calcPercent(prices[i],prices[i-1])
        if 0 < difference:
            avgUp += difference
        else:
            avgDown += -(difference)
        i += 1

    avgUp = calcDivision(avgUp,14)
    avgDown = calcDivision(avgDown,14)

    rs = calcDivision(avgUp,avgDown)
    rsi = 100 - calcDivision(100,(1+rs))

    return rsi

def calcMacd(prices):
    ema1 = calcEMA(prices,12)
    ema2 = calcEMA(prices,26)

    i=0
    macd =[]
    while i < len(ema2):
        macd.append(ema1[i+14]-ema2[i])
        i+=1

    return macd

def calcMaxMacd(macd, signal):
    signalI = len(macd)-len(signal)

    startH = []
    endH = []
    startL = []
    endL = []

    startPointL = None
    endPointL = None
    startPointH = None
    endPointH = None

    i = 0
    while(i < len(macd)-signalI):
        macdPoint = macd[i+signalI]
        signalPoint = signal[i]

        if(macdPoint > signalPoint):
            startPointH = i+signalI
            endPointL = i+signalI

            if startPointL != None and endPointL != None:
                startL.append(startPointL)
                endL.append(endPointL)
                startPointL = None
                endPointL = None

        elif(macdPoint < signalPoint):
            endPointH = i+signalI
            startPointL = i+signalI

            if startPointH != None and endPointH != None:
                startH.append(startPointH)
                endH.append(endPointH)
                startPointH = None
                endPointH = None

        i += 1

    listValues = 0
    i = 0
    while(i < len(startL)):
        list = macd[startL[i]:endL[i]]
        listValues += max(list)

        i += 1

    values = []
    values.append(calcDivision(listValues,i))

    listValues = 0
    i = 0
    while (i < len(startH)):
        list = macd[startH[i]:endH[i]]
        listValues += max(list)

        i += 1

    values.append(calcDivision(listValues,i))

    return values

def calcSMA(prices, period=0):
    i = 0
    sma = 0
    if period != 0:
        prices = prices[-period:]

        while i < period-1:
            sma += prices[i]
            i+=1

        sma = calcDivision(sma,period)
    else:
        while i < len(prices):
            sma += prices[i]
            i+=1
        sma = calcSMA(sma,len(prices))

    return sma

def calcEMA(prices,period):
    multiplier = calcDivision(2,(period + 1))

    i = period-1
    ema = []
    while i < len(prices):
        if i == period - 1:
            sma = calcSMA(prices, period)
            ema.append((prices[i] - sma) * multiplier + sma)
            x = 0
        else:
            ema.append((prices[i] - ema[x]) * multiplier + ema[x])
            x+=1
        i+=1

    return ema

def calcStop(prices, period):
    prices = prices[-period:]
    stop = min(prices) - 1 - random.random()

    return stop

def calcHigh(prices, period):
    prices = prices[-period:]
    high = max(prices)

    return high

def calcPercent(new,old):
    percent = (calcDivision((new - old), old)) * 100

    return percent

def calcDivision(dividend, divisor):
    if dividend != 0 and divisor != 0:
        result = dividend / divisor
    else:
        result = 0

    return result