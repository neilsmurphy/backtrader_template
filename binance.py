from ccxtbt import CCXTStore
import backtrader as bt
from datetime import datetime, timedelta, timezone
import json


class TestStrategy(bt.Strategy):
    def __init__(self):
        pass
        # self.sma = bt.indicators.SMA(self.data, period=21)

    def next(self):

        # Get cash and balance
        # New broker method that will let you get the cash and balance for
        # any wallet. It also means we can disable the getcash() and getvalue()
        # rest calls before and after next which slows things down.

        # NOTE: If you try to get the wallet balance from a wallet you have
        # never funded, a KeyError will be raised! Change LTC below as approriate
        # if self.live_data:
        #     cash, value = self.broker.get_wallet_balance('USDT')
        # else:
        #     # Avoid checking the balance during a backfill. Otherwise, it will
        #     # Slow things down.
        #     cash = value = 'NA'


        for data in self.datas:
            print(
                f"{data.datetime.datetime()},"
                f"{data._name},"
                # f"{cash}, {value}, "
                f"{data.open[0]}, "
                f"{data.high[0]}, "
                f"{data.low[0]}, "
                f"{data.close[0]}, "
                f"{data.volume[0]}, "
                # f"{self.sma[0]} "
            )

    def notify_data(self, data, status, *args, **kwargs):
        dn = data._name
        dt = datetime.utcnow().replace(tzinfo=timezone.utc)
        msg = "Data Status: {}".format(data._getstatusname(status))
        print(dt, dn, msg)
        if data._getstatusname(status) == "LIVE":
            self.live_data = True
        else:
            self.live_data = False


with open("./params.json", "r") as f:
    params = json.load(f)

cerebro = bt.Cerebro(quicknotify=True)


# Add the strategy
cerebro.addstrategy(TestStrategy)

#
# # Create our actual binance store
# config = {
#           "apiKey": params["binance_actual"]["apikey"],
#           "secret": params["binance_actual"]["secret"],
#           "enableRateLimit": True,
#           }

# Create our binance/testnet store
config = {'urls': {'api': 'https://testnet.binance.vision/api'},
    "apiKey": params["binance_testnet"]["apikey"],
    "secret": params["binance_testnet"]["secret"],
    "enableRateLimit": True,
}


# IMPORTANT NOTE - Kraken (and some other exchanges) will not return any values
# for get cash or value if You have never held any BNB coins in your account.
# So switch BNB to a coin you have funded previously if you get errors
store = CCXTStore(
    exchange="binance", currency="USDT", config=config, retries=5, debug=False, sandbox=True
)


# Get the broker and pass any kwargs if needed.
# ----------------------------------------------
# Broker mappings have been added since some exchanges expect different values
# to the defaults. Case in point, Kraken vs Bitmex. NOTE: Broker mappings are not
# required if the broker uses the same values as the defaults in CCXTBroker.
broker_mapping = {
    "order_types": {
        bt.Order.Market: "market",
        bt.Order.Limit: "limit",
        bt.Order.Stop: "stop-loss",  # stop-loss for kraken, stop for bitmex
        bt.Order.StopLimit: "stop limit",
    },
    "mappings": {
        "closed_order": {"key": "status", "value": "closed"},
        "canceled_order": {"key": "result", "value": 1},
    },
}

broker = store.getbroker(broker_mapping=broker_mapping)
cerebro.setbroker(broker)

# Get our data
# Drop newest will prevent us from loading partial data from incomplete candles
hist_start_date = datetime.utcnow() - timedelta(minutes=30)

data = store.getdata(
    dataname="BNB/USDT",
    name="BNBUSDT",
    timeframe=bt.TimeFrame.Minutes,
    fromdate=hist_start_date,
    # todate=datetime(2021, 7, 15),
    compression=1,
    ohlcv_limit=500,
    drop_newest=True,
    historical=False,
)

# Add the feed
cerebro.adddata(data)

# Run the strategy
cerebro.run()
