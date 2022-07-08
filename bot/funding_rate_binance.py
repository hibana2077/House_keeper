import ccxt,time,datetime
from discord import Webhook, RequestsWebhookAdapter
from timeit import default_timer as timer


WEBHOOK_URL = ''#your discord webhook url
webhook = Webhook.from_url(WEBHOOK_URL, adapter=RequestsWebhookAdapter())#webhook send message
API_KEY='' #your binance API_KEY
API_SECRET='' #your binance API_SECRET


MODE = 'normal'#change mode here normal or hedge


#init binancee future
binance = ccxt.binance({
    'apiKey': API_KEY,
    'secret': API_SECRET,
    'options': {
        'defaultType': 'future',
    },
})
binance.load_markets()

USDT_BASE=[t for t in binance.symbols if t.endswith('USDT')]


def get_funding_rate(symbol):#check done!
    temp=binance.fetch_funding_rate(symbol=symbol)
    return (temp['fundingRate']*100,temp['symbol'])

def get_symbol_price(symbol):#check done!
    temp=binance.fetch_ticker(symbol)
    return float(temp['last'])

def get_unrelazed_orders():#check done!
    balance = binance.fetch_balance()
    cc=0
    recorder={}
    for t in balance['info']['positions']:
        if float(t['unrealizedProfit'])>0 or float(t['unrealizedProfit'])<0:
            print(t['symbol'],t['unrealizedProfit'])
            recorder[t['symbol']]=(float(t['unrealizedProfit']),float(t['positionAmt']),float(t['entryPrice']))
            cc+=1
    webhook.send(content='尚未平倉數:'+str(cc))
    if cc==0:
        global order_counter
        order_counter=0
    return recorder


def get_unrelazed_orders_hedge():#return symbol amount and positionSide
    balance = binance.fetch_balance()
    cc=0
    recorder={}
    for t in balance['info']['positions']:
        if float(t['unrealizedProfit'])>0 or float(t['unrealizedProfit'])<0:
            print(t['symbol'],t['unrealizedProfit'])
            recorder[t['symbol']]=(float(t['unrealizedProfit']),t['positionSide'],float(t['positionAmt']),float(t['entryPrice']))
            cc+=1
    print('尚未平倉數:'+str(cc))
    return recorder


def search_high_funding_rate():#check done!
    s=timer()
    print('searching~')
    do=[]
    for t in USDT_BASE:
        temp=get_funding_rate(t)
        if abs(float(temp[0]))>0.08:
            webhook.send(content='高額度幣別:'+t+' '+str(temp[0])+'%'+'預計獲利:'+str(temp[0]-0.08)+'%')
            print(t,temp[0])
            do.append([t,temp[0]])
        elif abs(float(temp[0]))<=0.08:
            webhook.send(content='中額度幣別:'+t+' '+str(temp[0]))
            print(t,temp[0])
        else:pass
    e=timer()
    do = sorted(do, key=lambda x: abs(float(x[1])), reverse=True)
    print('searching done~',e-s,'s')
    return do

def place_limit_order_normal(symbol,side,price,amount):#not hedge
    try:
        temp=binance.create_order(symbol,type='limit',side=side,price=price,amount=amount)
        return temp
    except Exception as e:
        print(e)
        return None

def place_limit_order_hedge(symbol,side,price,amount,positionSide):#hedge
    try:
        params = {
            'positionSide': positionSide,
        }
        temp=binance.create_order(symbol,type='limit',side=side,price=price,amount=amount,params=params)
        return temp
    except Exception as e:
        print(e)
        return None

def place_market_order_normal(symbol,side,amount):#not hedge
    try:
        temp=binance.create_order(symbol,type='market',side=side,amount=amount)
        return temp
    except Exception as e:
        print(e)
        return None

def place_market_order_hedge(symbol,side,amount,positionSide):#hedge
    try:
        params = {
            'positionSide': positionSide,
        }
        temp=binance.create_order(symbol,type='market',side=side,amount=amount,params=params)
        return temp
    except Exception as e:
        print(e)
        return None

#not hedge mode only use buy and sell
#hedge mode use buy and sell and long and short(long and short is position side)


#hedge mode open position
#long:buy,short:sell
#hedge mode close position
#long:sell,short:buy
def brain():
    if MODE=='normal':
        print('normal mode')
        do=search_high_funding_rate()#return do[symbol,funding_rate]
        for t in do:
            symbol = t[0]
            symbol_price = float(binance.fetch_ticker(symbol)['last'])
            if t[1]<0 and symbol_price<=10:
                print('BUY',t)
                amount = int(10/symbol_price)
                order_price = symbol_price+(float(get_tick_size(symbol))*2)
                place_limit_order_normal(symbol,'BUY',order_price,amount)
            elif t[1]>0 and symbol_price<=10:
                print('SELL',t)
                amount = int(10/symbol_price)
                order_price = symbol_price-(float(get_tick_size(symbol))*2)
                place_limit_order_normal(symbol,'SELL',order_price,amount)
            else:
                print('nothing',t)
    elif MODE=='hedge':
        print('hedge mode')
        do=search_high_funding_rate()#return do[symbol,funding_rate]
        for t in do:
            symbol = t[0]
            symbol_price = float(binance.fetch_ticker(symbol)['last'])
            if t[1]<0 and symbol_price<=10:
                print('BUY',t)
                amount = int(10/symbol_price)
                order_price = symbol_price+(float(get_tick_size(symbol))*2)
                place_limit_order_hedge(symbol,'BUY',order_price,amount,'LONG')
            elif t[1]>0 and symbol_price<=10:
                print('SELL',t)
                amount = int(10/symbol_price)
                order_price = symbol_price-(float(get_tick_size(symbol))*2)
                place_limit_order_hedge(symbol,'SELL',order_price,amount,'SHORT')
            else:
                print('nothing',t)#超過預算不做交易
    else:
        print('mode has error!')

def auto_close_profit_order():
    if MODE =='normal':
        print('normal mode')
        do=get_unrelazed_orders()#recorder[t['symbol']]=(t['unrealizedProfit'],t['positionAmt'],t['entryPrice'])
        for t in do:#t will be symbol
            symbol_price = float(binance.fetch_ticker(t)['last'])
            if do[t][0]>abs(do[t][1])*do[t][2]*0.0008:#profit>commsion
                if do[t][1]>0 and symbol_price>do[t][2]:
                    print('SELL',t)
                    place_market_order_normal(t,'SELL',do[t][1])
                elif do[t][1]<0 and symbol_price<do[t][2]:
                    print('BUY',t)
                    place_market_order_normal(t,'BUY',do[t][1])
            else:
                print('nothing',t)
    elif MODE=='hedge':
        print('hedge mode')
        do=get_unrelazed_orders_hedge()#recorder[t['symbol']]=(t['unrealizedProfit'],t['positionSide'],t['positionAmt'],t['entryPrice'])
        for t in do:
            if do[t][0]>abs(do[t][2])*do[t][3]*0.0008:
                if do[t][1]=='LONG' and get_symbol_price(t)>=do[t][3]:
                    print('SELL',t)
                    place_market_order_hedge(t,'SELL',do[t][2],do[t][1])
                elif do[t][1]=='SHORT' and get_symbol_price(t)<=do[t][3]:
                    print('BUY',t)
                    place_market_order_hedge(t,'BUY',do[t][2],do[t][1])
            else:
                print('nothing',t)
    return None

def get_tick_size(symbol):return binance.market(symbol)['info']['filters'][0]['tickSize']


if __name__ == '__main__':
    print("HI")
    webhook.send("HI!")
    global order_counter
    order_counter=0
    while True:
        try:
            UTC = datetime.datetime.utcnow()
            CST = UTC + datetime.timedelta(hours=8)
            if (CST.hour==7 and CST.minute==59) or (CST.hour==15 and CST.minute==59) or (CST.hour==23 and CST.minute==59) and order_counter==0:
                brain()
                order_counter=1
            # time not in 7:59,15:59,23:59
            elif (CST.hour!=7 and CST.hour!=15 and CST.hour!=23) and (CST.minute!=59) and order_counter==1:
                auto_close_profit_order()
                time.sleep(2)
        except Exception as e:
            print(e)
            webhook.send(content=str(e))
            time.sleep(1)
            continue    
#to-do:

