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
from __future__ import absolute_import, division, print_function, unicode_literals
import collections
import datetime
from datetime import datetime, timedelta
import inspect
import itertools
import multiprocessing
import os
import sys
import time
import uuid

import backtrader as bt
from tabulate import tabulate

import extension.indicator as id
from extension.indicator import SmaCross
from extension.analyzer import AddAnalyzer
from extension.result import result
from extension.sizer import Stake
from extension.strategy import StandardStrategy
from utils import clear_database, df_to_db, yes_or_no


class RunBacktest:
    """
    Manages the execution of Backtrader backtests.

    - Manages parameters.
    - Creates all possible scenarios from the loaded lists.
    - Executes single or multiple backtest.
    - Manages multi-processing.
    - Loads cerebro and data, adds strategies, brokers etc.

    params:
      - ``pvalue`` (dict: default None)
          Dictionary with default values for the parameters in the first
          position in the list of the params dictionary.

      - ``dimension`` (dict: default None)
          Dictionary with dimension bool setting for output parameters.
          Dimension just indicates which parameters will be included when
          creating outputs to either results spreadsheets or plots. Located
          in the second position of the params dictionary.

      - ``print_params`` (bool: default ``False``)
          Print to terminal parameters at the beginning of the test.

      - ``run_test_now`` (bool: default ``True``)
          Will execute the test if true, if not just print parameters to terminal.

      - ``multi_pro`` (bool: default ``False``)
          Execute backtest using multi-processng.

      - ``reset_database`` (bool: default ``False``)
          If using a database, clear the database.

      Following are the params values contained in the params dictionary:
      - ``batchname`` (str: default ``None``)
          Custom batch name for identifying the backest in results.

      - ``batch_runtime`` (datetime: default ``now``)
          Time of batch execution.

      - ``db_name`` (str: default)
          Name of database.

      - ``test_number`` (UUID: )
          Truncated UUID number, calculated. Unique identifier.

      - ``save_result`` (bool: default ``False``)
          Analyzer outputs saved to excel/database.

      - ``save_excel`` (bool: default ``False``)
          Save to excel work book.

      - ``save_db`` (bool: default ``False``)
          Save results to database.

      - ``full_export`` (bool: default True)
          The analyzers are split into to groups. The first group has analyzers
          that only have one or minimal lines of output per test. The second group
          ``full`` has analyzer outputs that have many lines per backtest, such as
          OHLCV analyzer. Selecting full gives greater detail in the analyzer
          outputs, but slows down the backtests. This is most important when
          running many backtest as memory can become an issues. Try to use
          False for running many backtest. Which analyzers are included where
          can be modified in the ``AddAnalyzer.add_analyzers`` in
          ``extension.analyzer``.

      - ``save_path`` (str: default ``result``)
          Directory name where to save spreadsheet results. Created if none exist.

      - ``excluded_dates`` (list of dates: ``YYYY-MM-DD`` default ``None``)
          Use to exclude any specific dates in the backtest.

      - ``save_name`` (str: default ``result``)
          Root name for the excel results file. Combined with part of test_number.

      - ``from_date`` (str: ``YYYY-MM-DD`` default ``2020-01-01``)
          Hard start date, loading data from this date.

      - ``trade_start`` (str: ``YYYY-MM-DD`` default ``None``)
          Optional trade starting date.

      - ``to_date`` (str: ``YYYY-MM-DD`` default ``2020-12-31``)
          End of test date.

      - ``duration`` (int: default ``None`)
          Can be combined with ``trade_start`` to determine the end of test date.
          Usefull when conducting multi-tests with multiple start dates.

      - ``instrument`` (str: default ``None``)
          Symbol for the backtest if required. Some data is loaded without symbol.
          Some data uses the symbol  (e.g. Yahoo) to fetch the data.

      - ``benchmark`` (str: default ``None``)
          May be used to add a second dataline to the backtest primarily for outputting
          to compare results to a benchmark.

      - ``initinvestment`` (int: default ``10000``)
          Initial cash investment to start the backtest.

      - ``commission`` (float: default ``0.`` )
          Backtrader commission.

      - ``margin`` (float default ``None``)
          Backtrader margin.

      - ``mult`` (int: default ``50``)
          Multiplier if used in futures.

      - ``print_dev`` (bool: default ``False``)
          In the ``extension.strategy`` module ``StandardStrategy`` class
          there is a ``print_dev`` method. Use this for printing any ad hoc
          outputs.

      - ``print_orders_trades`` (bool: default ``False``)
          Print orders and trades.

      - ``printon`` (bool: default False)
          Minimal start and endpoint printing.

      - ``print_ohlcv`` (int: default -1),
          Prints the OHLCV of any data line. Use an integer to define the line.
          ``0`` for the first line, ``1`` for the next, etc. ``-1`` is off.

      - ``print_final_output`` (bool: default als)
          Prints to terminal the trade list, but any output may be added at
          the end of ``run_strat`` in this class.

      - ``ploton`` (bool: default ``False``)
          Print the backtrader plot.

    Custom params:
    Params that were used for this specific test and indicators. One can add
    conditions in the ``scenario`` method to ensure certain conditions are met
    in each ``scene``.
      - ``sma_period`` (int: default ``200``)
          Simple moving average.

      - ``limit_price`` (float: default ``.08``),
          Bracket orders limit price price adjuster. eg: close * (1 + ``.08``)

      - ``stop_price`` (float: default ``.04``),
          Bracket orders stop price price adjuster. eg: close * (1 - ``.04``)

      - ``trade_size`` (float: default ``1.``)
          Number of shares to trade. Should add a sizer if desired.
    """

    def __init__(
        self,
        pvalue=None,
        dimension=None,
        print_params=False,
        run_test_now=True,
        multi_pro=False,
        reset_database=False,
    ):

        # GENERAL BACKTEST SETTINGS
        self.print_params = print_params
        self.run_test_now = run_test_now
        self.multi_pro = multi_pro
        self.reset_database = reset_database

        self.params = dict(
            batchname=["None", True],
            batch_runtime=[datetime.now().strftime("%Y-%m-%d %H:%M"), False],
            db_name=[os.getenv("db_name"), False],
            test_number=[0, True],
            save_result=[False, False],
            save_tearsheet=[False, False],
            save_excel=[False, False],
            save_db=[False, False],
            full_export=[True, False],
            save_path=["results", False],
            excluded_dates=[None, False],
            save_name=["results", False],
            from_date=["2020-01-01", True],
            trade_start=[None, True],
            to_date=["2020-12-31", True],
            duration=[None, False],
            instrument=["^GSPC", True],
            benchmark=[None, True],
            initinvestment=[10000, False],
            commission=[0.0, True],
            margin=[None, False],
            mult=[1, True],
            print_dev=[False, False],
            print_orders_trades=[False, False],
            printon=[False, False],
            print_ohlcv=[-1, False],
            print_final_output=[False, False],
            ploton=[False, False],
            sma_fast=[20, True],
            sma_slow=[100, True],
            limit_price=[0.08, True],
            stop_price=[0.04, True],
            trade_size=[1.0, True],
        )

        # Create and modify the parameters values dictionary
        self.params_value = {p: v[0] for p, v in self.params.items()}

        if pvalue:
            self.params_value.update(pvalue)

        # Create and modify the parameters dimension dictionary.
        self.params_dimension = {p: v[1] for p, v in self.params.items()}

        if dimension:
            self.params_dimension.update(pvalue)

    def db_cols(self):
        return [d for d, v in self.params_dimension.items() if v]

    def get_attributes(self, cls):
        """ Gets the attributes from the class. """
        attributes = inspect.getmembers(cls, lambda a: not (inspect.isroutine(a)))
        return {
            a[0]: a[1]
            for a in attributes
            if not (a[0].startswith("__") and a[0].endswith("__"))
        }

    def all_params(self):
        """
        Returns all of the parameters for a backtest. Used in the strategy class
        to establish the params to be used.
        :returns All of the Parameters -> tuple:
        """
        # Retrieve the backtests main parameters.
        params = self.params_value

        # Get all of the classes create in the indicator module and then collect
        # their attributes.
        clsmembers = inspect.getmembers(
            sys.modules[id.__name__],
            lambda member: inspect.isclass(member) and member.__module__ == id.__name__,
        )

        for cls in clsmembers:
            try:
                params.update(self.get_attributes(cls[1].__dict__["params"]))
            except:
                pass

        return tuple([(k, v) for k, v in params.items()])

    def run_backtest(self):
        """Function for controlling the running of the backtests."""

        # Call a reset function from utilities.
        if self.reset_database:
            if yes_or_no("Do you wish to reset the database?"):
                clear_database()
            else:
                pass

        start_time = time.time()

        # Combinations of all the possible scenarios.
        scenarios, test_params = self.scenario()
        total_backtests = len(scenarios)

        # Print parameters
        if self.print_params:
            for k, v in test_params.items():
                if type(v) == str:
                    v_print = f'"{v}"'
                else:
                    v_print = v
                print(f"    {k}={v_print},")
            print("\n")

        # Run backtests, either single or multiple processor.
        if self.run_test_now:
            if self.multi_pro:
                # multiprocessing.freeze_support() # Used on windows machines.
                start_test = time.time()
                pool = multiprocessing.Pool(processes=multiprocessing.cpu_count() - 2)
                cum_backtest = 0
                backtest_with_trades = 0

                # This loop allows for processing to database backtest
                # results while further tests are still running. Saves memory.
                for agg_dict in pool.imap_unordered(
                    self.backtest_controller_multi, scenarios
                ):
                    if (
                        self.params_value["save_result"]
                        and self.params_value["save_db"]
                        and agg_dict is not None
                    ):
                        df_to_db(agg_dict)
                        backtest_with_trades += 1
                    cum_backtest += 1
                    print(
                        f"Backtests: {cum_backtest:3.0f} / {total_backtests:3.0f} "
                        f"backtests with trades {cum_backtest:3.0f} -- "
                        f"Elapsed: {(time.time() - start_test):.2f}"
                    )
                pool.close()

            else:
                # Single call to run backtest sequentially, no multi-processing.
                return self.backtest_controller(scenarios)

            end_time = time.time()
            print(f"\nElapsed time of {(end_time - start_time):.2f}")

    def backtest_controller(self, scenarios):
        """
        Runs multiple backtests sequentially one at a time. No multi processing.
        :param scenarios dict: Contains list of individual backtest ``scenes``.
        :return None:
        """

        # Loop though each backtest parameters.
        loop = 1
        for scene in scenarios:
            if scene['printon']:
                print("Starting loop {}".format(loop))
            loop += 1
            scene["test_number"] = str(uuid.uuid4()).replace("-", "")[:10]

            # Run the main strategy
            res, final_value = self.run_strat(scene)

            # If there are transactions, save results spreadsheet.
            if scene["save_result"]:
                if len(res[0].analyzers.getbyname("transactions").get_analysis()) > 0:
                    scene["db_cols"] = self.db_cols()
                    if scene["save_excel"] or scene["save_db"]:
                        agg_dict = result(res, scene, scene["test_number"])
                    if scene["save_db"]:
                        df_to_db(agg_dict)

            if scene["printon"]:
                print(f"Final value {final_value:.2f}")

        return final_value

    def backtest_controller_multi(self, scene=None):
        """
        Runs a single backtest controlled by multi processor.
        :param scene dict: One set of backtest parameters.
        :return agg_dict dict: Back test results if saving.
        """
        # Assign uniq id for the backtest to allow matching in database.
        scene["test_number"] = str(uuid.uuid4()).replace("-", "")[:10]

        # Run the main strategy and retrieving the strategy object
        # and final value.
        res, final_value = self.run_strat(scene)

        if scene["save_result"] and (scene["save_excel"] or scene["save_db"]):
            scene["db_cols"] = self.db_cols()
            agg_dict = result(res, scene, scene["test_number"])
            return agg_dict

    def iterize(self, iterable):
        """
        Handy function which turns things into things that can be iterated upon
        including iterables (source: backtrader cerebro.py)
        """
        niterable = list()
        for elem in iterable:
            if isinstance(elem, str):
                elem = (elem,)
            elif not isinstance(elem, collections.abc.Iterable):
                elem = (elem,)

            niterable.append(elem)

        return niterable

    def scenario(self):
        """
        Create list of all possible kwargs for running multiple backtests.
        Returns a dictionary of all the possible combinations of parameters
        for multiple backtests.

        Also returns one list of prameters with the individual inputs to create the
        scenarios. This is used for printing to terminal to  show the user the setup.

        :returns scenarios, test_params:
        """

        test_params = self.params_value.copy()
        excluded_dates = test_params.pop("excluded_dates")

        keys = test_params.keys()
        values = self.iterize(test_params.values())

        scenario_dict = [
            dict(zip(keys, combination)) for combination in itertools.product(*values)
        ]

        scenario_dict_final = list()
        for scenario in scenario_dict:
            if scenario["duration"]:
                end_date = datetime.strptime(
                    scenario["from_date"], "%Y-%m-%d"
                ) + timedelta(days=scenario["duration"])
                scenario["to_date"] = end_date.strftime("%Y-%m-%d")

                scenario["trade_start"] = scenario["from_date"]

            else:
                if not scenario["trade_start"]:
                    scenario["trade_start"] = scenario["from_date"]

            if excluded_dates:
                scenario["excluded_dates"] = excluded_dates
            else:
                scenario["excluded_dates"] = None

            if scenario["sma_fast"] >= scenario["sma_slow"]:
                continue

            scenario_dict_final.append(scenario)
        if scenario['printon']:
            print("There will be {} backtests run.\n".format(len(scenario_dict_final)))

        return scenario_dict_final, test_params

    def run_strat(self, scene):
        """
        Sets up and runs a back test.

        :param scene: Dictionary containing all parameters.
        :return: Cerebro strategy object and total value.
        """

        # Cerebro create
        cerebro = bt.Cerebro(stdstats=False)

        if scene["printon"]:
            print(
                "Running back test: loading data from {} with trading starts on {} to "
                "{}.\nLoading data...".format(
                    scene["from_date"], scene["trade_start"], scene["to_date"]
                )
            )
        else:
            pass

        # Get data from yahoo.
        for ticker in [scene["instrument"], scene["benchmark"]]:
            if ticker:
                data = bt.feeds.YahooFinanceData(
                    dataname=ticker,
                    timeframe=bt.TimeFrame.Days,
                    fromdate=datetime.strptime(scene["from_date"], "%Y-%m-%d"),
                    todate=datetime.strptime(scene["to_date"], "%Y-%m-%d"),
                    reverse=False,
                )

                cerebro.adddata(data)

        # Strategy
        cerebro.addstrategy(Strategy, **scene)

        # Broker
        cerebro.broker = bt.brokers.BackBroker()


        # Sizer
        cerebro.addsizer(Stake)

        # Cash
        cerebro.broker.setcash(scene["initinvestment"])
        cerebro.broker.setcommission(
            commission=scene["commission"], margin=scene["margin"], mult=scene["mult"]
        )

        # Analyzers
        cerebro = AddAnalyzer(cerebro).add_analyzers()

        # Cerebro run
        strat = cerebro.run(tradehistory=True)

        # Print out the final result
        if scene["printon"]:
            print("\n\nFinal Portfolio Value: %.2f" % cerebro.broker.getvalue())
        else:
            pass

        # Print trade lists to the terminal.
        if scene["print_final_output"]:
            trade_list = strat[0].analyzers.getbyname("trade_list").get_analysis()
            if len(trade_list):
                for t in trade_list:
                    t["datein"] = t["datein"].strftime("%Y-%m-%d %H:%M")
                    t["dateout"] = t["dateout"].strftime("%Y-%m-%d %H:%M")
                print(tabulate(trade_list, headers="keys"))
            else:
                print("There were no completed trades.")

        # Plot if requested to.
        if scene["ploton"]:
            cerebro.plot()

        return strat, cerebro.broker.getvalue()


class Strategy(StandardStrategy):
    """
    This is a Custom Backtrader strategy class for RunBacktest engine. It is
    an extension of Standard_Strategy which can be found in the
    extension/strategy_base.py.

    Strategy classes have one or more indicators to provide information such as
    buy and sell signals plus other information. These can be loaded from the
    extension/indicator.py file. Each indicator should produce a buy sell
    that can be combined with othe buy sell signals to create final buy-long,
    sell-short signals for trading.

    All parameters are managed in the extensions.scenarios module.
    """

    # Creates a tuple of all the parameters for the ``strategy`` class.
    params = RunBacktest().all_params()

    def __init__(self):
        super().__init__()
        self.ord = None

        self.sma_cross = SmaCross(sma_fast=self.p.sma_fast, sma_slow=self.p.sma_slow)

        self.long_buy_signal = self.sma_cross.long_buy_signal
        self.short_sell_signal = self.sma_cross.short_sell_signal

    def next(self):
        # Printouts for dev. To become logging.
        if self.p.print_dev:
            self.print_dev()

        # Current bar datetime, date, and time.
        dt = self.data.datetime.datetime()
        date = self.data.datetime.date()
        time = self.data.datetime.time()

        # Check if the trade date is less than the set trade start date.
        # If so, return, no action.
        if date < datetime.strptime(self.p.trade_start, "%Y-%m-%d").date():
            return

        if self.p.print_ohlcv > -1:
            # Print out the OHLC. -1 means no print, 0 or greater indicates the
            # dataline to print.
            self.print_signal(self.p.print_ohlcv)

        # Trading strategy.
        if self.ord:
            return

        if self.long_buy_signal and self.getposition().size <= 0:
            limit_price = self.datas[0].close[0] * (1 + self.p.limit_price)
            stop_price = self.datas[0].close[0] * (1 - self.p.stop_price)
            size = (self.broker.get_value() * 0.9) / self.datas[0].close[0]

            order = self.buy_bracket(
                size=size,
                exectype=bt.Order.Market,
                stopprice=stop_price,
                stopexec=bt.Order.Stop,
                limitprice=limit_price,
                limitexec=bt.Order.Limit,
            )

            self.ord = [o for o in order]
