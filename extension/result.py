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
import pandas as pd
from pathlib import Path
import quantstats as qs
import xlsxwriter
import yfinance as yf

"""
Module for converting the standard indicator dictionaries exported in the strategy 
object at the end of a Backtrader backtest. 
"""

def add_key_to_df(df, test_number):
    """ Inserts the key columns at the beginning of the dataframe"""
    df.insert(0, "test_number", test_number)
    return df


def tradelist(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    This analyzer prints a list of trades similar to amibroker, containing MFE and MAE

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    trade_list = analyzer[0]
    if scene["save_db"]:
        df = pd.DataFrame(trade_list)
        df.columns = [x.replace("%", "_pct") for x in df.columns]
        df = add_key_to_df(df, test_number)
        agg_dict["trade_list"] = df

    if scene["save_excel"]:
        worksheet = workbook.add_worksheet("trade_list")
        columns = trade_list[0].keys()
        columns = [x.capitalize() for x in columns]
        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("D:D", sheet_format["x_wide"], None)
        worksheet.set_column("E:E", sheet_format["narrow"], sheet_format["float_2d"])
        worksheet.set_column("F:F", sheet_format["x_wide"], None)
        worksheet.set_column("G:G", sheet_format["narrow"], sheet_format["float_2d"])
        worksheet.set_column("H:H", sheet_format["narrow"], sheet_format["percent"])
        worksheet.set_column("I:I", sheet_format["narrow"], sheet_format["int_0d"])
        worksheet.set_column("J:J", sheet_format["narrow"], sheet_format["percent"])
        worksheet.set_column("L:M", sheet_format["narrow"], sheet_format["int_0d"])
        worksheet.set_column("O:O", sheet_format["narrow"], sheet_format["int_0d"])
        worksheet.set_column("P:P", sheet_format["narrow"], sheet_format["percent"])
        worksheet.set_column("Q:Q", sheet_format["narrow"], sheet_format["percent"])

        for i, d in enumerate(trade_list):
            d["datein"] = d["datein"].strftime("%Y-%m-%d %H:%M")
            d["dateout"] = d["dateout"].strftime("%Y-%m-%d %H:%M")

            worksheet.write_row(i + 1, 0, d.values())

    return workbook, agg_dict


def tradeclosed(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Closed trades, pnl, commission, and duration.
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    trade_dict = analyzer.get_analysis()

    columns_df = [
        "Date Closed",
        "Ticker",
        "PnL",
        "PnL Comm",
        "Commission",
        "Days Open",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(trade_dict)
        df = df.T
        df.columns = columns_df
        df = add_key_to_df(df, test_number)
        agg_dict["trade"] = df

    if scene["save_excel"]:
        columns = [
            "Date Closed",
            "Time",
            "Ticker",
            "PnL",
            "PnL Comm",
            "Commission",
            "Days Open",
        ]

        worksheet = workbook.add_worksheet("trade")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["wide"], None)
        worksheet.set_column("B:B", sheet_format["medium"], None)
        worksheet.set_column("D:E", sheet_format["narrow"], sheet_format["float_2d"])
        worksheet.set_column("F:F", sheet_format["medium"], sheet_format["int_0d"])
        worksheet.set_column("G:G", sheet_format["medium"], sheet_format["float_5d"])

        for i, value in enumerate(trade_dict.values()):
            worksheet.write_row(i + 1, 0, [value[0].strftime("%Y-%m-%d")])
            worksheet.write_row(i + 1, 1, [value[0].strftime("%H:%M")])
            worksheet.write_row(i + 1, 2, value[1:])

    return workbook, agg_dict


def transactions(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Returns the transactions dataframe.
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    trans_dict = analyzer.get_analysis()
    columns_df = ["Date", "Units", "Price", "SID", "Ticker", "Value"]

    if scene["save_db"]:
        li = []
        for k, v in trans_dict.items():
            rec = tuple([k, v[0][0], v[0][1], v[0][2], v[0][3], v[0][4]])
            li.append(rec)
        df = pd.DataFrame(li, columns=columns_df)
        df = add_key_to_df(df, test_number)
        agg_dict["transaction"] = df

    if scene["save_excel"]:
        columns = ["Date", "Units", "Price", "SID", "Ticker", "Value"]

        worksheet = workbook.add_worksheet("transaction")
        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["x_wide"], None)
        worksheet.set_column("C:C", sheet_format["medium"], sheet_format["float_2d"])
        worksheet.set_column("E:F", sheet_format["medium"], sheet_format["float_2d"])

        dates = []
        trans = []
        for d, v in trans_dict.items():
            for t in v:
                dates.append(d)
                trans.append(t)

        for n in range(len(dates)):
            date = [dates[n].strftime("%y-%m-%d %H:%M")]

            worksheet.write_row(n + 1, 0, date)
            worksheet.write_row(n + 1, 1, trans[n])

    return workbook, agg_dict


def unnest_trade_analysis(d, trade_analysis_dict, pk=""):
    """
    Recursive function that will create layered key names and attach the values.
    Used by the trade_analysis function.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            unnest_trade_analysis(v, trade_analysis_dict, pk + "_" + k)
        else:
            trade_analysis_dict[(pk + "_" + k)[1:]] = v


def tradeanalyzer(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    This is the trades analysis nested dictionary, converting to single row for insertion into table.
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    Return columns: There are many single point metrics available. Please refer to the following for reference.

    [
    'key',
    'total_total', 'total_open', 'total_closed',

    'streak_won_current', 'streak_won_longest', 'streak_lost_current', 'streak_lost_longest',

    'pnl_gross_total', 'pnl_gross_average', 'pnl_net_total', 'pnl_net_average',

    'won_total', 'won_pnl_total', 'won_pnl_average', 'won_pnl_max',

    'lost_total', 'lost_pnl_total', 'lost_pnl_average', 'lost_pnl_max',

    'long_total',
    'long_pnl_total', 'long_pnl_average',
    'long_pnl_won_total', 'long_pnl_won_average', 'long_pnl_won_max',
    'long_pnl_lost_total', 'long_pnl_lost_average', 'long_pnl_lost_max',
    'long_won', 'long_lost',

    'short_total',
    'short_pnl_total', 'short_pnl_average',
    'short_pnl_won_total', 'short_pnl_won_average', 'short_pnl_won_max',
    'short_pnl_lost_total', 'short_pnl_lost_average', 'short_pnl_lost_max',
    'short_won', 'short_lost',

    'len_total', 'len_average', 'len_max', 'len_min',
    'len_won_total', 'len_won_average', 'len_won_max', 'len_won_min',
    'len_lost_total', 'len_lost_average', 'len_lost_max', 'len_lost_min',
    'len_long_total', 'len_long_average', 'len_long_max', 'len_long_min',
    'len_long_won_total', 'len_long_won_average', 'len_long_won_max', 'len_long_won_min',
    'len_long_lost_total', 'len_long_lost_average', 'len_long_lost_max', 'len_long_lost_min',
    'len_short_total', 'len_short_average', 'len_short_max', 'len_short_min',
    'len_short_won_total', 'len_short_won_average', 'len_short_won_max', 'len_short_won_min',
    'len_short_lost_total', 'len_short_lost_average', 'len_short_lost_max', 'len_short_lost_min'
    ]
    """

    trades = analyzer.get_analysis()

    # Create empty dictionary for final keys:values, this will pass through recursive function unest_trade_analysis
    trade_analysis_dict = {}
    unnest_trade_analysis(trades, trade_analysis_dict, pk="")

    ta_cols = [
        "total_total",
        "total_open",
        "total_closed",
        "streak_won_current",
        "streak_won_longest",
        "streak_lost_current",
        "streak_lost_longest",
        "pnl_gross_total",
        "pnl_gross_average",
        "pnl_net_total",
        "pnl_net_average",
        "won_total",
        "won_pnl_total",
        "won_pnl_average",
        "won_pnl_max",
        "lost_total",
        "lost_pnl_total",
        "lost_pnl_average",
        "lost_pnl_max",
        "long_total",
        "long_pnl_total",
        "long_pnl_average",
        "long_pnl_won_total",
        "long_pnl_won_average",
        "long_pnl_won_max",
        "long_pnl_lost_total",
        "long_pnl_lost_average",
        "long_pnl_lost_max",
        "long_won",
        "long_lost",
        "short_total",
        "short_pnl_total",
        "short_pnl_average",
        "short_pnl_won_total",
        "short_pnl_won_average",
        "short_pnl_won_max",
        "short_pnl_lost_total",
        "short_pnl_lost_average",
        "short_pnl_lost_max",
        "short_won",
        "short_lost",
        "len_total",
        "len_average",
        "len_max",
        "len_min",
        "len_won_total",
        "len_won_average",
        "len_won_max",
        "len_won_min",
        "len_lost_total",
        "len_lost_average",
        "len_lost_max",
        "len_lost_min",
        "len_long_total",
        "len_long_average",
        "len_long_max",
        "len_long_min",
        "len_long_won_total",
        "len_long_won_average",
        "len_long_won_max",
        "len_long_won_min",
        "len_long_lost_total",
        "len_long_lost_average",
        "len_long_lost_max",
        "len_long_lost_min",
        "len_short_total",
        "len_short_average",
        "len_short_max",
        "len_short_min",
        "len_short_won_total",
        "len_short_won_average",
        "len_short_won_max",
        "len_short_won_min",
        "len_short_lost_total",
        "len_short_lost_average",
        "len_short_lost_max",
        "len_short_lost_min",
    ]

    columns = [
        "Item",
        "Value",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(
            trade_analysis_dict.values(), index=trade_analysis_dict.keys()
        )
        df = df.T
        df = add_key_to_df(df, test_number)
        fill_cols = [c for c in ta_cols if c not in df.columns]
        for c in fill_cols:
            df[c] = 0
        agg_dict["trade_analysis"] = df

    if scene["save_excel"]:
        worksheet = workbook.add_worksheet("trade_analysis")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:B", sheet_format["x_wide"], sheet_format["align_left"])

        for i, (k, v) in enumerate(trade_analysis_dict.items()):
            worksheet.write_row(i + 1, 0, [k])
            worksheet.write_row(i + 1, 1, [v])

    return workbook, agg_dict


def vwr(scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None):
    """
    Calculates Variability Weighted Return (VWR).
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the drawdowns auto ordered nested dictionary
    vwr_dict = analyzer.get_analysis()

    columns = [
        "vwr",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(vwr_dict.values(), index=vwr_dict.keys()).T
        df = add_key_to_df(df, test_number)
        agg_dict["vwr"] = df

    if scene["save_excel"]:

        worksheet = workbook.add_worksheet("vwr")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["x_wide"], sheet_format["align_left"])
        worksheet.set_column("B:B", sheet_format["medium"], sheet_format["align_left"])

        for i, (k, v) in enumerate(vwr_dict.items()):
            worksheet.write_row(i + 1, 0, [k])
            worksheet.write_row(i + 1, 1, [v])

    return workbook, agg_dict


def drawdown_analysis(d, drawdown_analysis_dict, pk=""):
    """
    Recursive function that will create layered key names and attach the values.
    """
    for k, v in d.items():
        if isinstance(v, dict):
            drawdown_analysis(v, drawdown_analysis_dict, pk + "_" + k)
        else:
            drawdown_analysis_dict[(pk + "_" + k)[1:]] = v

    return drawdown_analysis_dict


def drawdown(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Calculates drawdown information.
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the drawdowns auto ordered nested dictionary
    drawdown = analyzer.get_analysis()

    # Create empty dictionary for final keys:values
    drawdown_analysis_dict = {}
    drawdown_analysis_dict = drawdown_analysis(drawdown, drawdown_analysis_dict, pk="")

    columns = [
        "Item",
        "Value",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(
            drawdown_analysis_dict.values(), index=drawdown_analysis_dict.keys()
        ).T
        df = add_key_to_df(df, test_number)
        agg_dict["drawdown"] = df

    if scene["save_excel"]:

        worksheet = workbook.add_worksheet("drawdown")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["x_wide"], sheet_format["align_left"])
        worksheet.set_column("B:B", sheet_format["medium"], sheet_format["align_left"])

        for i, (k, v) in enumerate(drawdown_analysis_dict.items()):
            worksheet.write_row(i + 1, 0, [k])
            worksheet.write_row(i + 1, 1, [v])

    return workbook, agg_dict


def cashmarket(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Portfolio cash and total values.

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the stats auto ordered nested dictionary
    value = analyzer.get_analysis()

    columns = [
        "Date",
        "Cash",
        "Value",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(value)
        df = df.T
        df = df.reset_index()
        df.columns = columns
        df = add_key_to_df(df, test_number)
        agg_dict["value"] = df

    if scene["save_excel"]:

        worksheet = workbook.add_worksheet("value")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:C", sheet_format["wide"], sheet_format["float_2d"])

        for i, (k, v) in enumerate(value.items()):
            date = k.strftime("%y-%m-%d %H:%M")
            worksheet.write_row(i + 1, 0, [date])
            worksheet.write_row(i + 1, 1, v)

    return workbook, agg_dict


def positionvalue(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Tracks all positions over time.

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the stats auto ordered nested dictionary
    position = analyzer.get_analysis()

    if scene["save_db"]:
        df = pd.DataFrame(list(position.values())[1:], index=list(position.keys())[1:])
        df = df.reset_index()
        li = position["Datetime"]
        li.insert(0, "Datetime")
        df.columns = li
        df = add_key_to_df(df, test_number)
        agg_dict["positions"] = df

    if scene["save_excel"]:
        worksheet = workbook.add_worksheet("positions")

        columns_date = ["Date"]
        columns_row = position["Datetime"]

        worksheet.write_row(0, 0, columns_date)
        worksheet.write_row(0, 1, columns_row)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["wide"], None)
        worksheet.set_column("B:B", sheet_format["wide"], sheet_format["float_2d"])
        worksheet.set_column("C:ZZ", sheet_format["medium"], sheet_format["float_2d"])

        for i, (k, v) in enumerate(position.items()):
            if i == 0:
                continue

            date = k.strftime("%Y-%m-%d %H:%M")
            worksheet.write_row(i, 0, [date])
            worksheet.write_row(i, 1, v)

    return workbook, agg_dict


def ohlcv(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    OHLCV

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the stats auto ordered nested dictionary
    ohlcv = analyzer.get_analysis()

    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

    if scene["save_db"]:
        df = pd.DataFrame(ohlcv)
        df = df.T
        df = df.reset_index()
        df.columns = columns
        df = add_key_to_df(df, test_number)
        agg_dict["ohlcv"] = df

    if scene["save_excel"]:

        worksheet = workbook.add_worksheet("ohlcv")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["wide"], None)
        worksheet.set_column("B:E", sheet_format["narrow"], sheet_format["float_2d"])
        worksheet.set_column("F:F", sheet_format["medium"], sheet_format["int_0d"])

        for i, (k, v) in enumerate(ohlcv.items()):
            if i == 0:
                continue

            date = k.strftime("%Y-%m-%d %H:%M")
            worksheet.write_row(i, 0, [date])
            worksheet.write_row(i, 1, v)

    return workbook, agg_dict

def benchmark(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Benchmark Candles

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Get the stats auto ordered nested dictionary
    benchmark = analyzer.get_analysis()

    columns = ["Date", "Open", "High", "Low", "Close", "Volume"]

    if scene["save_db"]:
        df = pd.DataFrame(benchmark)
        df = df.T
        df = df.reset_index()
        df.columns = columns
        df = add_key_to_df(df, test_number)
        agg_dict["benchmark"] = df

    if scene["save_excel"]:

        worksheet = workbook.add_worksheet("benchmark")

        worksheet.write_row(0, 0, columns)

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:A", sheet_format["wide"], None)
        worksheet.set_column("B:E", sheet_format["narrow"], sheet_format["float_2d"])
        worksheet.set_column("F:F", sheet_format["medium"], sheet_format["int_0d"])

        for i, (k, v) in enumerate(benchmark.items()):
            if i == 0:
                continue

            date = k.strftime("%Y-%m-%d %H:%M")
            worksheet.write_row(i, 0, [date])
            worksheet.write_row(i, 1, v)

    return workbook, agg_dict

def globaloutput(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Global output details captured.
y
    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """

    global_out = analyzer.get_analysis()
    # columns_keys = ["datetime", "ma"]
    # columns_values = [k for k in global_out[next(iter(global_out))].keys()]

    if scene["save_db"]:
        df = pd.DataFrame(global_out).T
        if df.size == 0:
            pass
        df.index = df.index.set_names(["Datetime"])
        df = df.reset_index()
        df = add_key_to_df(df, test_number)
        agg_dict["global_out"] = df

    return workbook, agg_dict


def orderhistory(
    scene, analyzer, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Order history details captured.

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """

    order_history = analyzer.get_analysis()
    # columns_keys = ["datetime", "ma"]
    # columns_values = [k for k in global_out[next(iter(global_out))].keys()]

    if scene["save_db"]:
        df = pd.DataFrame(order_history).T
        if df.size == 0:
            pass
        df.index = df.index.droplevel(1)
        df.index.name = "Datetime"
        df = df.reset_index()
        df = add_key_to_df(df, test_number)
        agg_dict["order_history"] = df

    return workbook, agg_dict


def dimension(
    scene, results, test_number, workbook=None, sheet_format=None, agg_dict=None
):
    """
    Input parameters.

    :param workbook: Excel workbook to be saved to disk.
    :param analyzer: Backtest analyzer.
    :param sheet_format: Dictionary holding formatting information such as col width, font etc.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return workbook: Excel workbook to be saved to disk.
    """
    # Convert tuples to string in scene.
    # Convert tuples to strings.
    for t in [k for k, v in scene.items() if isinstance(v, tuple)]:
        scene[t] = ", ".join(["(" + x[0] + ", " + str(x[1]) + ")" for x in scene[t]])

    # Create the dimension dataframe.
    dimension_dict = {}
    db_cols = scene.pop("db_cols")
    dimension_dict.update(scene)

    columns = [
        "Item",
        "Value",
    ]

    if scene["save_db"]:
        df = pd.DataFrame(dimension_dict.values(), index=dimension_dict.keys())
        df = df.T
        df = df.loc[:, db_cols]
        agg_dict["dimension"] = df

    if scene["save_excel"]:
        worksheet = workbook.add_worksheet("dimension")

        worksheet.write_row(0, 0, columns)

        worksheet.write_row(1, 0, ["test number", test_number])

        worksheet.set_row(0, None, sheet_format["header_format"])

        worksheet.set_column("A:B", sheet_format["x_wide"], sheet_format["align_left"])

        for i, (k, v) in enumerate(dimension_dict.items()):
            if k == "excluded_dates":
                continue

            worksheet.write_row(i + 2, 0, [k])
            worksheet.write_row(i + 2, 1, [v])

    return workbook, agg_dict

def quantstats(scene, test_number, agg_dict):
    """
    Input parameters.

    :param scene: Dictionary with backtest parameters.
    :param test_number: Backtest test number.
    :param agg_dict: Collects the dictionary outputs from backtrader for using in platting.
    :return agg_dict: Updated agg_dict including dataframe quantstants for the backtest.
    """
    df = agg_dict["value"].copy()
    df = df.set_index("Date")["Value"]
    df.index = pd.to_datetime(df.index)

    df = qs.utils.to_returns(df)
    df_qs = qs.reports.metrics(df, display=False, mode="full")
    df_qs.columns = [test_number]
    df_qs = df_qs.T
    df_qs.index.name = "test_number"
    df_qs.columns = df_qs.columns.str.replace("%", "-pct")
    df_qs.columns = df_qs.columns.str.replace("(", "")
    df_qs.columns = df_qs.columns.str.replace(")", "")
    df_qs = df_qs.fillna(0)
    agg_dict["quantstats"] = df_qs.reset_index()
    return agg_dict




def tearsheet(scene, results):
    """
    Just for tearsheet.

    :param workbook: Excel workbook to be saved to disk.
    :return None: .
    """
    # Get the stats auto ordered nested dictionary
    value = results[0].analyzers.getbyname("cash_market").get_analysis()

    columns = [
        "Date",
        "Cash",
        "Value",
    ]

    if scene["save_tearsheet"]:
        # Save tearsheet
        df = pd.DataFrame(value)
        df = df.T
        df = df.reset_index()
        df.columns = columns

        df_value = df.set_index("Date")["Value"]
        df_value.index = pd.to_datetime(df_value.index)
        df_value = df_value.sort_index()
        value_returns = qs.utils.to_returns(df_value)
        value_returns = pd.DataFrame(value_returns)

        value_returns["diff"] = value_returns["Value"].diff().dropna()
        value_returns["diff"] = value_returns["diff"].abs().cumsum()
        value_returns = value_returns.loc[value_returns["diff"] > 0, "Value"]
        value_returns.index = pd.to_datetime(value_returns.index.date)

        # Get the benchmark
        benchmark = None
        bm_title = None
        bm = scene["benchmark"]
        if bm:
            df_benchmark = yf.download(
                bm,
                start=value_returns.index[0],
                end=value_returns.index[-1],
                auto_adjust=True,
            )["Close"]

            df_benchmark = qs.utils.rebase(df_benchmark)
            benchmark = qs.utils.to_returns(df_benchmark)
            benchmark.name = bm
            benchmark.index = pd.to_datetime(benchmark.index.date)
            bm_title = f"  (benchmark: {bm})"



        # df_combine = value_returns.join()
        # Set up file path.
        Path(scene["save_path"]).mkdir(parents=True, exist_ok=True)
        dir = Path(scene["save_path"])
        filename = (
                scene["save_name"]
                + "-"
                + scene["batchname"]
                + "-"
                + scene["batch_runtime"].replace("-", "").replace(":", "").replace(" ", "_")
                + ".html"
        )
        filepath = dir / filename

        title = f"{scene['batchname']}{bm_title if bm_title is not None else ''}"
        qs.reports.html(
            value_returns,
            benchmark=benchmark,
            title=title,
            output=filepath,
        )

def result(results, scene, test_number):
    """ Extraction of analyzer lines from dictionary form. """

    # If there are no transactions, return None and test number.
    if len(results[0].analyzers.getbyname("transactions").get_analysis()) == 0:
        print(f"{test_number} has no transactions.")
        return

    if scene["save_tearsheet"]:
        agg_dict = {}
        tearsheet(scene, results)

    if scene["save_db"] and not scene["save_excel"]:
        agg_dict = {}

        if scene["full_export"]:
            try:
                analyzer = (
                    results[0].analyzers.getbyname("trade_list").get_analysis(),
                )

                _, agg_dict = tradelist(
                    scene, analyzer, test_number, agg_dict=agg_dict,
                )
            except:
                pass

        for analyzer in results[0].analyzers:
            if scene["benchmark"] ==  None:
                if type(analyzer).__name__.lower() == "benchmark":
                    continue
            if scene["full_export"]:
                if type(analyzer).__name__.lower() == "tradelist":
                    continue
            elif not scene["full_export"]:
                if type(analyzer).__name__.lower() not in [
                    "drawdown",
                    "tradeanalyzer",
                    "vwr",
                    "cashmarket",
                    # "tradelist",
                ]:
                    continue

            try:
                _, agg_dict = eval(type(analyzer).__name__.lower())(
                    scene, analyzer, test_number, agg_dict=agg_dict
                )
            except:
                pass

        _, agg_dict = dimension(scene, results, test_number, agg_dict=agg_dict)

        agg_dict = quantstats(scene, test_number, agg_dict=agg_dict)

    elif scene["save_excel"]:

        path = Path(scene["save_path"])
        path.mkdir(parents=True, exist_ok=True)
        # test_params = get_test_params_indicator(test_number=scene["test_number"])
        # filename_ma_id = "-".join([x for x in test_params.keys()])
        filename = (
            scene["save_name"]
            + "-"
            + scene["test_number"]
            + "_"
            + "{}".format(test_number[:8])
            + ".xlsx"
        )
        filepath = path / filename

        # Create workbook.
        workbook = xlsxwriter.Workbook(filepath)

        # set parameters for saving.

        # Add some cell formats.
        # Column Widths
        sheet_format = dict(
            narrow=8,
            medium=12,
            wide=16,
            x_wide=20,
            header_format=workbook.add_format(
                {
                    "bold": True,
                    "text_wrap": True,
                    "valign": "top",
                    "align": "center",
                    "font_color": "black",
                    # "border": 1,
                }
            ),
            float_2d=workbook.add_format({"num_format": "#,##0.00"}),
            float_5d=workbook.add_format({"num_format": "#,##0.00000"}),
            int_0d=workbook.add_format({"num_format": "#,##0"}),
            percent=workbook.add_format({"num_format": "0%"}),
            align_left=workbook.add_format({"align": "left"}),
        )

        agg_dict = {}

        try:
            analyzer = (results[0].analyzers.getbyname("trade_list").get_analysis(),)

            workbook, agg_dict = tradelist(
                scene, analyzer, test_number, workbook, sheet_format, agg_dict,
            )
        except:
            pass

        for analyzer in results[0].analyzers:
            if type(analyzer).__name__.lower() == "tradelist":
                continue

            try:
                workbook, agg_dict = eval(type(analyzer).__name__.lower())(
                    scene, analyzer, test_number, workbook, sheet_format, agg_dict
                )
            except:
                pass

        workbook, agg_dict = dimension(
            scene, results, test_number, workbook, sheet_format, agg_dict
        )
        # agg_dict = ema_inputs_to_db(scene, test_number, agg_dict)

        workbook.close()

    return agg_dict
