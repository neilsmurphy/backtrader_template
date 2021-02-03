###############################################################################
#
# Software program written by Neil Murphy in year 2020.
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

class DummyInd(bt.Indicator):
    """ The dummy line sets an initial line for calculating indicators."""

    lines = ("dummyline",)
    params = (("dummyline_value", 1),)
    plotinfo = dict(plot=False)

    def __init__(self):
        self.lines.dummyline = bt.Max(0.0, self.params.dummyline_value)


class SmaCross(bt.Indicator):
    """ Sample indicator. """
    lines = ("long_buy_signal", "short_sell_signal",)
    params = (("sma_fast", 15), ("sma_slow", 100),)
    plotinfo = dict(plot=False)

    def __init__(self):
        """ Simple moving average cross up and down. """
        self.sma_fast = bt.ind.MovingAverageSimple(period=self.p.sma_fast)
        self.sma_slow = bt.ind.MovingAverageSimple(period=self.p.sma_slow)

        self.l.long_buy_signal = bt.ind.CrossUp(self.sma_fast, self.sma_slow)
        self.l.short_sell_signal = bt.ind.CrossDown(self.sma_fast, self.sma_slow)