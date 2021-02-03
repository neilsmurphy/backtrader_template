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

from main import RunBacktest

""" User module to setup test parameters and launch tests. """


# GENERAL SETTINGS
print_params = True
run_test_now = True
multi_pro = True
reset_database = True

# BACKTEST PARAMETERS
pvalues = dict(
    username='Chewbacca',
    batchname="Multi Test",
    from_date="2016-01-01",
    trade_start="2016-09-01",
    to_date="2019-12-31",
    # duration=500,
    instrument=["F", "TSLA", "AAPL", "FB", "V", "BAC"],
    benchmark="SPY",
    sma_fast=15, #list(range(15, 61, 15)),
    sma_slow=45, # list(range(30, 91, 15)),
    limit_price=.05, #[.025, .05, .075],
    stop_price=.05, # [.03, .05, .07, .09],
    trade_size=10,
    # TERMINAL OUTPUT
    print_dev=False,
    print_orders_trades=False,
    print_ohlcv=-1,  # `-1` for no print, otherwise feed the dataline number.
    print_final_output=False,
    printon=True,
    # SAVING
    save_result=True,
    save_excel=True,
    save_db=True,
    full_export=False,
)


set_bt = RunBacktest(
    pvalue=pvalues,
    print_params=print_params,
    run_test_now=run_test_now,
    multi_pro=multi_pro,
    reset_database=reset_database,
)

set_bt.run_backtest()
