#!c:\users\pcuser1.pcuser1-pc\appdata\local\programs\python\python38\python.exe

from kiteconnect import KiteConnect
import talib
import pandas as pd
#from datetime import datetime
import datetime
import os
import acctkn

att=acctkn.att()
ap=acctkn.atp()

kite = KiteConnect(api_key=ap)
kite.set_access_token(att)


print('Login SUCCESS')

nifty50 = ['TATAMOTORS','ULTRACEMCO','HDFCBANK','HDFC','GRASIM','LT','HINDALCO','UPL','MARUTI','M&M','BAJFINANCE','SBIN','BPCL','IOC','BHARTIARTL','SHREECEM','KOTAKBANK','SUNPHARMA','POWERGRID','NTPC','GAIL','HCLTECH','TCS','AXISBANK','COALINDIA','ITC','ONGC','BAJAJ-AUTO','INFY','EICHERMOT','NESTLEIND','TATASTEEL','DIVISLAB','WIPRO','ADANIPORTS','ASIANPAINT','CIPLA','ICICIBANK','JSWSTEEL','TECHM','TITAN','BRITANNIA','DRREDDY','SBILIFE','HINDUNILVR','INDUSINDBK','RELIANCE','HEROMOTOCO','BAJAJFINSV','HDFCLIFE']
#nifty50 = ['TATAMOTORS']
interval='5minute' #5 minute candle used
dayss = 4   #History number of days, it is a mininum 
slpct=0.005  #0.5% stop-loss 
tgtpct=0.005 #0.5% Target
trade_quantity = 1
traded = []


## it is not a bracket order
def def_place_mkt_order_buy(symbol,ltp,trade_quantity,sl_val,tgt_val):
 #print("Im inside def_place_mkt_order_buy")
 try:
    order_id = kite.place_order(tradingsymbol=symbol,variety=kite.VARIETY_REGULAR,
                                 exchange=kite.EXCHANGE_NSE,
                                 transaction_type=kite.TRANSACTION_TYPE_BUY,
                                 quantity=trade_quantity,
                                 order_type=kite.ORDER_TYPE_MARKET,
                                 product=kite.PRODUCT_MIS,price=None, validity=None, 
                                 disclosed_quantity=None, trigger_price=None, 
                                 squareoff=None, stoploss=None, trailing_stoploss=None, tag=None)
 
    print("Order placed. ID is:", order_id)
    return order_id
 except Exception as e:
    print("exception occured:" + str(e))


def def_place_mkt_order_sell(symbol,ltp,trade_quantity,sl_val,tgt_val):
 #print("Im inside def_place_mkt_order_sell for: ",symbol)
 try:
    order_id = kite.place_order(tradingsymbol=symbol,variety=kite.VARIETY_REGULAR,
                                 exchange=kite.EXCHANGE_NSE,
                                 transaction_type=kite.TRANSACTION_TYPE_SELL,
                                 quantity=trade_quantity,
                                 order_type=kite.ORDER_TYPE_MARKET,
                                 product=kite.PRODUCT_MIS,price=None, validity=None, 
                                 disclosed_quantity=None, trigger_price=None, 
                                 squareoff=None, stoploss=None, trailing_stoploss=None, tag=None)
 
    print("Order placed. ID is:", order_id)
    return order_id
 except Exception as e:
    print("exception occured:" + str(e))


def get_historic_data(name, timeframe, delta):
	to_date = datetime.datetime.now().date()
	from_date = to_date - datetime.timedelta(days=int(delta))
	token = kite.ltp(['NSE:' + name])['NSE:' + name]['instrument_token']
	data = kite.historical_data(token, from_date, to_date, timeframe)
	data = pd.DataFrame(data)
	return data


def apply_indicators(df,name):
	df['recent_volume30'] = talib.MA(df['volume'], timeperiod = 30, matype=0)
	df['average_volume120'] = talib.MA(df['volume'], timeperiod = 120, matype=0)
	df['rsi']  = talib.RSI(df['close'], timeperiod=14)
	filename = name + '.csv'
	df.to_csv(filename)
	return df

while True:
 print('Scanning started from Beginning')
 for symbol in nifty50:
  df = get_historic_data(symbol, interval, dayss)
  df = apply_indicators(df,symbol)
  last_candle_data = df.iloc[-1]
  #print('last_candle_data',last_candle_data)    
  last2_candle_data = df.iloc[-2]
  #print('last2_candle_data',last2_candle_data)    
  
  
  current_volume = last_candle_data['recent_volume30']
  average_volume = last_candle_data['average_volume120']
  rsi_last = last_candle_data['rsi']
  rsi_last_2nd = last2_candle_data['rsi']

  ## get the LTP price to calculate the TARGET & STOPLOSS
  ohlc=kite.ohlc('NSE:{}'.format(symbol))
  ltp = ohlc['NSE:{}'.format(symbol)]['last_price']  
  #print('printing ltp:',ltp)
  sl_val = round(ltp*(slpct/100),1)
  tgt_val = round(ltp*(tgtpct/100),1)
  #print(sl_val,tgt_val)

  ## don't take trade if already taken position.
  x=''
  for trade in traded:
   if trade == symbol:
    x='traded'
    break
 
  if( rsi_last_2nd < 80 and (rsi_last > 80) and current_volume > average_volume and x != 'traded' ):  
   traded.append(symbol)
   print(symbol,last_candle_data['date'],'current_volume',current_volume,'average_volume',average_volume,'rsi_last',rsi_last,'rsi_last_2nd',rsi_last_2nd)
   ord_id = def_place_mkt_order_buy(symbol,ltp,trade_quantity,sl_val,tgt_val)
   print('BUY entered for :',symbol,' & CURRENT TIME IS',datetime.datetime.now(),'ORDER_ID')
   #exit()
  elif ( rsi_last_2nd > 20 and (rsi_last < 20) and current_volume > average_volume and x != 'traded' ):
   print(symbol,last_candle_data['date'],'current_volume',current_volume,'average_volume',average_volume,'rsi_last',rsi_last,'rsi_last_2nd',rsi_last_2nd)
   traded.append(symbol)
   ord_id = def_place_mkt_order_sell(symbol,ltp,trade_quantity,sl_val,tgt_val)
   print('SELL entered for :',symbol,' & CURRENT TIME IS',datetime.datetime.now(),'ORDER_ID')
   #exit()
  else:
   print('No indication for', symbol,' & CURRENT TIME IS',datetime.datetime.now())