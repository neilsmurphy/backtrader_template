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

from main import RunBacktest

""" User module to setup test parameters and launch tests. """

# GENERAL SETTINGS
print_params = True
run_test_now = True
multi_pro = False
reset_database = False

# BACKTEST PARAMETERS
pvalues = dict(
    batchname="Single Test",
    from_date="2016-01-01",
    trade_start="2016-09-01",
    to_date="2020-12-31",
    # duration=500,
    initinvestment=100000,
    instrument= "FB",
    benchmark="SPY",
    sma_fast=30,
    sma_slow=45,
    limit_price=0.07,
    stop_price=0.05,
    # TERMINAL OUTPUT
    print_dev=False,
    print_orders_trades=True,
    print_ohlcv=-1,  # `-1` for no print, otherwise feed the dataline number.
    print_final_output=True,
    printon=True,
    # SAVING
    save_path="result",
    save_name="my test name",
    save_result=False,
    save_excel=True,
    save_tearsheet=True,
    save_db=False,
    full_export=True,
)

set_bt = RunBacktest(
    pvalue=pvalues,
    print_params=print_params,
    run_test_now=run_test_now,
    multi_pro=multi_pro,
    reset_database=reset_database,
)

set_bt.run_backtest()
