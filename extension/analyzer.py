###############################################################################
#
# Software program written by Neil Murphy in year 2021.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# By using this software, the Disclaimer and Terms distributed with the
# software are deemed accepted, without limitation, by user.
#
# You should have received a copy of the Disclaimer and Terms document
# along with this program.  If not, see... https://bit.ly/2Tlr9ii
#
###############################################################################
import backtrader as bt


class GlobalOutput(bt.analyzers.Analyzer):
    """ Capture output from the custom global indicators that are active.   """

    def start(self):
        self.rets = {}

    def next(self):
        st = self.strategy

        global_values = dict()

        # Long Buy/Short Sell signals.

        d = dict(
            open=st.datas[0].open[0],
            high=st.datas[0].high[0],
            low=st.datas[0].low[0],
            close=st.datas[0].close[0],
            volume=st.datas[0].volume[0],
        )
        global_values.update(d)

        try:
            d = dict(
                long_buy_signal=st.long_buy_signal[0],
                short_sell_signal=st.short_sell_signal[0],
            )
            global_values.update(d)
        except:
            pass


        self.rets[self.data.datetime.datetime()] = global_values

    def get_analysis(self):
        return self.rets


class TradeList(bt.analyzers.Analyzer):
    """
    Trade list similar to Amibroker output: Columns are:
    [ref, ticker, dir, datein, pricein, dateout, priceout, chng%,
    pnl, pnl%, size, value, cumpnl, nbars, pnl/bar, mfe%, mae%]

    Courtesy of ab_trader.
    https://github.com/ab-trader/backtrader_addons/blob/master/
    backtrader_addons/analyzers/trade_list.py
    """

    def get_analysis(self):

        return self.trades

    def __init__(self):
        self.trades = []
        self.cumprofit = 0.0

    def notify_trade(self, trade):

        if trade.isclosed:

            brokervalue = self.strategy.broker.getvalue()

            dir = "short"
            if trade.history[0].event.size > 0:
                dir = "long"

            pricein = trade.history[len(trade.history) - 1].status.price
            priceout = trade.history[len(trade.history) - 1].event.price
            datein = bt.num2date(trade.history[0].status.dt).date()
            dateout = bt.num2date(trade.history[len(trade.history) - 1].status.dt).date()

            # if trade.data._timeframe >= bt.TimeFrame.Days:
            #     datein = datein.date()
            #     dateout = dateout.date()

            pcntchange = 100 * priceout / pricein - 100
            pnl = trade.history[len(trade.history) - 1].status.pnlcomm
            pnlpcnt = 100 * pnl / brokervalue
            barlen = trade.history[len(trade.history) - 1].status.barlen
            try:
                pbar = pnl / barlen
            except:
                pbar = 0
            self.cumprofit += pnl

            size = value = 0.0
            for record in trade.history:
                if abs(size) < abs(record.status.size):
                    size = record.status.size
                    value = record.status.value

            highest_in_trade = max(trade.data.high.get(ago=0, size=barlen + 1))
            lowest_in_trade = min(trade.data.low.get(ago=0, size=barlen + 1))
            hp = 100 * (highest_in_trade - pricein) / pricein
            lp = 100 * (lowest_in_trade - pricein) / pricein
            if dir == "long":
                mfe = hp
                mae = lp
            if dir == "short":
                mfe = -lp
                mae = -hp

            self.trades.append(
                {
                    "ref": trade.ref,
                    "ticker": trade.data._name,
                    "dir": dir,
                    "datein": datein,
                    "pricein": pricein,
                    "dateout": dateout,
                    "priceout": priceout,
                    "chng%": round(pcntchange, 2),
                    "pnl": pnl,
                    "pnl%": round(pnlpcnt, 2),
                    "size": size,
                    "value": value,
                    "cumpnl": self.cumprofit,
                    "nbars": barlen,
                    "pnl/bar": round(pbar, 2),
                    "mfe%": round(mfe, 2),
                    "mae%": round(mae, 2),
                }
            )


class OrderHistory(bt.analyzers.Analyzer):
    """ Analyzer for tracking details of outstanding orders at each bar. """

    def start(self):
        self.rets = {}

    def next(self):
        st = self.strategy
        dt = self.data.datetime.datetime()

        if len(st.broker.orders) == 0:
            return

        for o in st.broker.orders:
            try:
                if o.status < 4:
                    order_detail = dict(
                        ref=o.ref,
                        status=o.status,
                        # finished=finished,
                        ordtype=o.OrdTypes[o.ordtype],
                        price=o.created.price,
                        size=o.size,
                        valid=o.valid,
                    )

                    self.rets[(dt, o.ref,)] = order_detail
            except:
                pass

    def get_analysis(self):
        return self.rets


class CashMarket(bt.analyzers.Analyzer):
    """
    Analyzer returning cash and market values
    """

    def __init__(self):
        self.current_date = None

    def start(self):
        super(CashMarket, self).start()

    def create_analysis(self):
        self.rets = {}
        self.vals = 0.0

    def notify_cashvalue(self, cash, value):
        date = self.data.datetime.date()
        if date != self.current_date:
            self.vals = (cash, value)
            self.rets[self.strategy.datetime.datetime()] = self.vals
            self.current_date = date
        else:
            pass

    def get_analysis(self):
        return self.rets


class TradeClosed(bt.analyzers.Analyzer):
    """
    Analyzer returning closed trade information.
    """

    def start(self):
        super(TradeClosed, self).start()

    def create_analysis(self):
        self.rets = {}
        self.vals = tuple()

    def notify_trade(self, trade):
        """Receives trade notifications before each next cycle"""
        if trade.isclosed:
            self.vals = (
                self.strategy.datetime.datetime(),
                trade.data._name,
                round(trade.pnl, 2),
                round(trade.pnlcomm, 2),
                trade.commission,
                (trade.dtclose - trade.dtopen),
            )
            self.rets[trade.ref] = self.vals

    def get_analysis(self):
        return self.rets


class OHLCV(bt.analyzers.Analyzer):
    """

    This analyzer reports the OHLCV of each of datas.

    Params:
      - timeframe (default: ``None``)
        If ``None`` then the timeframe of the 1st data of the system will be
        used
      - compression (default: ``None``)
        Only used for sub-day timeframes to for example work on an hourly
        timeframe by specifying "TimeFrame.Minutes" and 60 as compression
        If ``None`` then the compression of the 1st data of the system will be
        used
    Methods:
      - get_analysis
        Returns a dictionary with returns as values and the datetime points for
        each return as keys
    """

    def start(self):
        # tf = min(d._timeframe for d in self.datas)
        # self._usedate = bt.TimeFrame.Seconds
        self.rets = {}

    def next(self):
        # Create custom volume for plotting higher volumes in bright yellow,
        # grey out lower volume.

        try:
            self.rets[self.datas[0].datetime.datetime()] = [
                self.datas[0].open[0],
                self.datas[0].high[0],
                self.datas[0].low[0],
                self.datas[0].close[0],
                self.datas[0].volume[0],
            ]
        except:
            pass

    def get_analysis(self):
        return self.rets


class Benchmark(bt.analyzers.Analyzer):
    """ This analyzer reports the Benchmark of each. """

    def start(self):
        self.rets = {}

    def next(self):
        # Create custom volume for plotting higher volumes in bright yellow,
        # grey out lower volume.

        try:
            self.rets[self.datas[0].datetime.datetime()] = [
                self.datas[1].open[0],
                self.datas[1].high[0],
                self.datas[1].low[0],
                self.datas[1].close[0],
                self.datas[1].volume[0],
            ]
        except:
            pass

    def get_analysis(self):
        return self.rets


class AddAnalyzer:
    """
    Adds the analyzers to cerebro and returns cerebro to the ``run_strat``.
    """
    def __init__(self, cerebro):
        self.cerebro = cerebro

    def add_analyzers(self):
        # Analyzers. Custom analyzers can be found in extensions/analyzer.py
        # Analyzers returned in the strategy object
        scene = self.cerebro.strats[0][0][2]
        # self.cerebro.addanalyzer(
        #     bt.analyzers.VariabilityWeightedReturn,
        #     _name="VWR",
        #     timeframe=bt.TimeFrame.Days,
        #     tau=2.0,
        #     sdev_max=0.2,
        # )

        # For all tests, but mainly high volume multi-processor tests.
        self.cerebro.addanalyzer(bt.analyzers.TradeAnalyzer, _name="trades")
        self.cerebro.addanalyzer(bt.analyzers.DrawDown, _name="drawdown")
        self.cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
        self.cerebro.addanalyzer(CashMarket, _name="cash_market")
        self.cerebro.addanalyzer(TradeList, _name="trade_list")

        # Enable these analyzers only if full expert used for plotting
        # individual backtests.
        if scene["full_export"]:
            self.cerebro.addanalyzer(bt.analyzers.Transactions, _name="transactions")
            self.cerebro.addanalyzer(TradeClosed, _name="trade_closed")
            self.cerebro.addanalyzer(OHLCV, _name="OHLCV")
            self.cerebro.addanalyzer(Benchmark, _name="benchmark")
            self.cerebro.addanalyzer(GlobalOutput, _name="global_signal")
            self.cerebro.addanalyzer(OrderHistory, _name="order_history")



        return self.cerebro
