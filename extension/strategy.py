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

class StandardStrategy(bt.Strategy):

    """
    This is a standard strategy. Each ``strategy`` class will inherit from here.
    """

    def log(self, txt):
        """ Logging function for this strategy. """
        dt = self.datetime.date()
        print(f"{dt}, {txt}")

    def notify_order(self, order):
        """ Triggered upon changes to orders. """

        # Suppress notification if it is just a submitted order.
        if order.status == order.Submitted:
            return

        # Print out the date, security name, order number and status.
        dt, dn = self.datetime.date(), order.data._name
        if self.p.print_orders_trades:
            type = "Buy" if order.isbuy() else "Sell"
            self.log(
                f"Order {order.ref:3d},\tType {type},\tStatus {order.getstatusname()} \t"
                f"Size: {order.created.size:9.4f}, Price: {order.created.price:9.4f}, "
            )
        if order.status == order.Margin:
            return

        # Check if an order has been completed
        if order.status in [order.Completed]:
            if self.p.print_orders_trades:
                self.log(
                    f"{'BUY' if order.isbuy() else 'SELL'} EXECUTED for {dn}, "
                    f"Price: {order.executed.price:6.2f}, "
                    f"Cost: {order.executed.value:6.2f}, "
                    f"Comm: {order.executed.comm:4.2f}, "
                    f"Size: {order.created.size:9.4f}, "
                )

        if len([o for o in self.ord if o.status < 4]) == 0:
            self.ord = list()

    def notify_trade(self, trade):
        """Provides notification of closed trades."""
        if trade.isclosed:
            if self.p.print_orders_trades:
                self.log(
                    "{} Closed: PnL Gross {}, Net {},".format(
                        trade.data._name, round(trade.pnl, 2), round(trade.pnlcomm, 1),
                    )
                )
            else:
                pass

    def print_signal(self, dataline):
        """ Print out OHLCV. """
        self.log(
            "o {:5.2f}\th {:5.2f}\tl {:5.2f}\tc {:5.2f}\tv {:5.0f}".format(
                self.datas[dataline].open[0],
                self.datas[dataline].high[0],
                self.datas[dataline].low[0],
                self.datas[dataline].close[0],
                self.datas[dataline].volume[0],
            )
        )

    def print_dev(self):
        """ For development logging. """

        # Change as needed.
        self.log(
            f"Value: {self.broker.cash:5.2f}, "
            f"Cash: {self.broker.get_value():5.2f}, "
            f"Close:{self.datas[1].close[0]:5.2f}, "
        )

