"""
@author: rakeshr
"""
"""
Websocket client that streams data of all strikes contract 
for requested option symbol 
"""

import json, logging, asyncio, time
from multiprocessing import Process, Queue
from kiteconnect import KiteConnect, KiteTicker
from optionchain_stream.instrument_file import InstrumentMaster
from optionchain_stream.implied_vol import implied_volatility
import datetime

def assign_callBacks(*args):
    # Assign all the callbacks
    print("Assigning start")
    # websocket_obj.kws.on_ticks = websocket_obj.on_ticks
    # websocket_obj.kws.on_connect = websocket_obj.on_connect
    # websocket_obj.kws.on_close = websocket_obj.on_close
    # websocket_obj.kws.on_error = websocket_obj.on_error
    # websocket_obj.kws.on_noreconnect = websocket_obj.on_noreconnect
    # websocket_obj.kws.on_reconnect = websocket_obj.on_reconnect
    # logging.debug("kws.connect()")
    # websocket_obj.kws.connect()


class WebsocketClient(object):
    def __init__(self, api_key, api_secret, access_token, symbol, expiry):
        # Create kite connect instance
        logging.basicConfig(level=logging.DEBUG)
        print("ininit!")
        self.kite = KiteConnect(api_key=api_key)
        # self.data = self.kite.generate_session(request_token, api_secret=api_secret)
        self.kws = KiteTicker(api_key, access_token, debug=True,reconnect=False)
        self.symbol = symbol
        self.expiry = expiry
        # self.instrumentClass = InstrumentMaster(api_key)
        # self.instrumentClass = instrument_class
        # self.token_list = self.instrumentClass.fetch_contract(self.symbol, str(self.expiry))
        # logging.debug(self.token_list)
        self.q = Queue()
        # Set access_token for Quote API call
        self.kite.set_access_token(access_token)

    def form_option_chain(self, q):
        """
        Wrapper method around fetch and create option chain
        """
        while 1:
            complete_option_data = self.instrumentClass.generate_optionChain(self.token_list)
            # Store queue data 
            q.put(complete_option_data)

    def on_ticks(self, ws, ticks):
        """
        Push each tick to DB
        """   
        for tick in ticks:
            contract_detail = self.instrumentClass.fetch_token_detail(tick['instrument_token'])
            expiry_date = datetime.datetime.strptime(self.expiry, '%Y-%m-%d')
            # calculate time difference from contract expiry
            time_difference = (expiry_date - datetime.datetime.today()).days
            contract = 'NSE:{}'.format(contract_detail['name'])
            # fetch underlying contract ltp from Quote API call
            eq_detail = self.kite.quote([contract])
            # Calculate IV
            if contract_detail['type'] == 'CE':
                iv = implied_volatility('CALL', eq_detail[contract]['last_price'], contract_detail['strike'], time_difference,
                                             0.04, tick['last_price'])
            elif contract_detail['type'] == 'PE':
                iv = implied_volatility('PUT', eq_detail[contract]['last_price'], contract_detail['strike'], time_difference,
                                             0.04, tick['last_price'])
            optionData = {'token':tick['instrument_token'], 'symbol':contract_detail['symbol'], 
                                'last_price':tick['last_price'], 'volume':tick['volume'], 'change':tick['change'],
                                'oi':tick['oi'], 'iv':iv}
            # Store each tick to redis with symbol and token as key pair
            logging.debug(contract_detail['symbol'])
            logging.debug(tick['instrument_token'])
            logging.debug(optionData)
            self.instrumentClass.store_option_data(contract_detail['symbol'], tick['instrument_token'], optionData)

    def on_connect(self, ws, response):
        # self.token_list = InstrumentMaster("",self.kite).fetch_contract(self.symbol, str(self.expiry))
        ws.subscribe(self.token_list)
        ws.set_mode(ws.MODE_FULL, self.token_list)
        logging.debug("on_connect")

    def on_close(self, ws, code, reason):
        logging.error("closed connection on close: {} {}".format(code, reason))
        logging.debug("on_close")

    def on_error(self, ws, code, reason):
        logging.error("closed connection on error: {} {}".format(code, reason))

    def on_noreconnect(self, ws):
        logging.error("Reconnecting the websocket failed")

    def on_reconnect(self, ws, attempt_count):
        logging.debug("Reconnecting the websocket: {}".format(attempt_count))
    
    def assign_callBacks(self,api_key):
        # Assign all the callbacks
        self.instrumentClass = InstrumentMaster(api_key)
        # self.instrumentClass = instrument_class
        self.token_list = self.instrumentClass.fetch_contract(self.symbol, str(self.expiry))
        logging.debug(self.token_list)

        logging.debug("Assigning start")
        self.kws.on_ticks = self.on_ticks
        self.kws.on_connect = self.on_connect
        self.kws.on_close = self.on_close
        self.kws.on_error = self.on_error
        self.kws.on_noreconnect = self.on_noreconnect
        self.kws.on_reconnect = self.on_reconnect
        logging.debug("kws.connect()")
        self.kws.connect()

    def new_fun(*args):
        print("new fun!")
        print(args)

    def queue_callBacks(self,api_key,api_secret, access_token, symbol, expiry,):
        """
        Wrapper around ticker callbacks with multiprocess Queue
        """
        # Process to keep updating real time tick to DB
        # Process(target=self.new_fun,args=(api_key,api_secret, access_token, 
            # symbol, expiry,)).start()
        Process(target=self.assign_callBacks,args=(api_key,)).start()
        # self.assign_callBacks()
        # Delay to let intial instrument DB sync
        # For option chain to fetch value
        # Required only during initial run
        # time.sleep(2)
        # Process to fetch option chain in real time from Redis
        # Process(target=self.form_option_chain,args=(self.q, )).start()