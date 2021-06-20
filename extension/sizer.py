import math
import backtrader as bt

class Stake(bt.Sizer):

	params = (('stake', 1),)

	def _getsizing(self, comminfo, cash, data, isbuy):
		if isbuy:
			divide = math.floor((cash * .9)/data.close[0])
			self.p.stake = divide
			return self.p.stake

		# Sell situation
		position = self.broker.getposition(data)
		if not position.size:
			return 0  # do not sell if nothing is open

		return self.p.stake