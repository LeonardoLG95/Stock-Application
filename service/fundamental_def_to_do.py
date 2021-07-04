def getTreasuryNote(year=0):
    import pandas_datareader as web
    from datetime import date

    today = date.today()
    today = today.strftime('%Y-%m-%d')
    try:
        tn = web.DataReader('^TNX', data_source='yahoo', start=today, end=today)
    except:
        print('Error al descargar las notas del tesoro de 10 de america')

    tn = tn['Close'][-1]
    tn = float(tn)

    return tn

def getInflationRate(year):
    import pandas_datareader as web
    from datetime import date

    today = date.today()
    today = today.strftime('%Y-%m-%d')
    try:
        ir = web.DataReader('CPI', data_source='yahoo', start=today, end=today)
    except:
        print('Error al descargar la inflacción de america')

    ir = ir['Close'][-1]
    ir = float(ir)

    print(ir)

    return ir

def calcRiskFreeRate():
    # get treasure note
    gbr = getTreasuryNote()
    # get inflation rate
    ir = 0
    rfr = ((1+gbr)/(1+ir))-1

    return rfr

def CAPM():
    '''
    Valoración por descuento de flujos (para saber si una acción esta bien de precio)(capm)
    Calcular flujo de caja para el invesionista CAPM (en base a 10 años):

        Para calcularlo:
        CAPM = Risk-Free Rate + (Beta * Market Risk Premium):
            Risk-Free Rate:
                =((1+Government Bond Rate)/(1+Inflation Rate)-1)
                Por lo que he leído en wallstreetmojo.com,
                para plazos hasta 1 año se usan treasury bills(t-bills).
                para plazos de 1 a 10 años treasure note.
                para plazos de más de 10 años treasure bond.
            Beta:
                =

            Market Risk Premium:
                =

    :return:
    '''

def analizeAnnualBalance(ticker):

    from yahoofinancials import YahooFinancials as yf
    import pandas as pd

    yahoo_financials = yf(ticker)
    dic = yahoo_financials.get_financial_stmts('annual','balance')
    '''
    Último dato no se sabe que fecha será la de publicación 
    con lo que hay que buscar la primera key del diccionario 
    ya que con [0] no vale
    '''
    dic = dic['balanceSheetHistory'][ticker][0]
    keys = list(dic.keys())
    year = keys[0]
    dic = dic[year]
    dic = pd.DataFrame(dic.items())
    print('-----------------------------',year,'-----------------------------')
    print(dic)