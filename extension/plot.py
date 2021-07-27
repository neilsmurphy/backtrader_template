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
import pandas as pd

import plotly
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots


pd.options.display.max_rows = 500
pd.set_option("precision", 2)
pd.set_option("display.float_format", lambda x: "%.3f" % x)

from utils import create_db_connection

class backtest_plot:
    """ Returns plotly plot figures for use in dashboards.

    Used for one backtest. Data is gathered from the backtest database and
    used to generate plots for the dashboard.



    """
    def __init__(self):
        self.start_plot_date = self.get_start_plot_date()
        self.dfs = self.get_plot_data()

    def get_connection(self):
        return create_db_connection(db="live")

    def get_start_plot_date(self):
        with self.get_connection() as conn:
            sql = f"SELECT * FROM next;"
            df = pd.read_sql(sql, con=conn)
        return df["Date"].min()

    def get_plot_data(self):
        # Get all of the data required for a backtest plot.
        table_names = [
            # "order_history",
            "next",
            # "global_out",
            # "drawdown",
            # "trade",
            # "trade_analysis",
            # "trade_list",
            # "transaction",
            # "value",
            # todo add quantstats?
        ]

        dfs = {}
        for table_name in table_names:
            with self.get_connection() as conn:
                try:
                    sql = f"SELECT * FROM {table_name};"
                    df = pd.read_sql(sql, con=conn)
                except:
                    raise ValueError(
                        f"There were no records for table {table_name}. This is likely due "
                        f"to a lack of closed transactions.")
            if "Date" in df.columns:
                df.rename(columns={'Date': 'Datetime'}, inplace=True)

            # Format date fields.
            if table_name in ["next", "ohlcv", "value"]:
                df = df.set_index("Datetime")
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
            elif table_name == "global_out":
                df = df.set_index("Datetime")
                df.index = pd.to_datetime(df.index)
                df = df.sort_index()
                df.index = pd.to_datetime(df.index)
                df = df.dropna(axis=1, how='all')
                df = df.dropna(axis=0, how='any')
                try:
                    df = df.loc[self.start_plot_date:, :]
                except:
                    pass
                df = df.reset_index()
            elif table_name == 'trade_list':
                df['datein'] = pd.to_datetime(df['datein'])
                df['dateout'] = pd.to_datetime(df["dateout"])

            dfs[table_name] = df

        return dfs

    def set_layout(self):
        # Set layout
        layout = dict(
            title=dict(
                text=f"Dashboard",
                font=dict(family="Oveerpass", size=18,),  # color="firebrick"),
            ),
            xaxis=(dict(type="category", rangeslider=dict(visible=False), showgrid=False)),
            yaxis=(dict(showgrid=False)),
            xaxis2=(dict(type="category", showgrid=False)),
            yaxis2=(dict(showgrid=False)),
            xaxis3=(dict(type="category", showgrid=False)),
            yaxis3=(dict(showgrid=False)),
            showlegend=True,
            legend=dict(
                title=dict(text="Lines", font=dict(family="arial", size=15)),
                borderwidth=5,
                font=dict(family="Balto", size=12),
                orientation="v",
                x=1,
                xanchor="left",
                y=1,
                yanchor="top",
            ),
            template="plotly_dark",
            hovermode="closest",
            margin=dict(l=120, r=120, t=120, b=120),
            autosize=True,
            width=1400,
            height=800,
            clickmode="none",
            dragmode="pan",
            selectdirection="h",
        )
        return layout

    def ohlc(self, df=None):
        """ Plot data for OHLC """
        if df is None:
            df = self.dfs["next"]
        df = df.reset_index()
        fig = go.Figure(
            data=[
                go.Candlestick(
                    name="ES Mini",
                    x=df["Datetime"],
                    open=df["Open"],
                    high=df["High"],
                    low=df["Low"],
                    close=df["Close"],
                )
            ]
        )
        return fig
        # return fig.add_trace(fig_ohlc.data[0], row=1, col=1)

    def trade_list(self, df=None):
        if df is None:
            df = self.dfs["trade_list"]
        df['datein'] = pd.to_datetime(df['datein'])
        df['dateout'] = pd.to_datetime(df['dateout'])

        long_color = "orange"
        short_color = "purple"
        twof = ":5.2f"
        threef = ":5.3f"
        boolf = ":2.0f"
        tl_cols = {
            "chng_pct": threef,
            "pnl": threef,
            "pnl_pct": threef,
            "size": boolf,
            "value": twof,
            "cumpnl": boolf,
            "nbars": threef,
            "pnl/bar": threef,
            "mfe_pct": threef,
            "mae_pct": threef,
        }
        # hover template string
        template_string = "<br>"
        for i, (col, fmt) in enumerate(tl_cols.items()):
            t_string = col + "=%{customdata[" + str(i) + "]" + fmt + "}<br>"
            template_string += t_string

        # Trade in
        fig = px.scatter(
            df,
            x=df["datein"],
            y="pricein",
            color="dir",
            hover_data=[k for k in tl_cols.keys()],
            category_orders={"dir": ["long", "short"]},
        )

        long_short_category = df["dir"].unique()

        for ls in long_short_category:
            if ls == "long":
                marker_color = long_color
                n = 0
            elif ls == "short":
                marker_color = short_color
                n = len(long_short_category) - 1

            fig.data[n].marker.symbol = 8
            fig.data[n].marker.size = 15
            fig.data[n].marker.color = marker_color
            fig.data[n].hovertemplate = template_string
            # fig.append_trace(fig.data[n], row=1, col=1)


        # Trade out
        fig_out = px.scatter(
            df,
            x=df["dateout"],
            y="priceout",
            color="dir",
            hover_data=[k for k in tl_cols.keys()],
            category_orders={"dir": ["long", "short"]},
        )

        for ls in long_short_category:
            if ls == "long":
                marker_color = long_color
                n = 0
            elif ls == "short":
                marker_color = short_color
                n = len(long_short_category) - 1

            fig_out.data[n].marker.symbol = 7
            fig_out.data[n].marker.size = 15
            fig_out.data[n].marker.color = marker_color
            fig_out.data[n].hovertemplate = template_string
            fig.append_trace(fig_out.data[n], row=1, col=1)

        return fig

    # def order_history(self, df=None):
    #     if df is None:
    #         df = self.dfs["order_history"]
    #     df = df.set_index("Datetime")
    #     df.index = pd.to_datetime(df.index)
    #     df = df.sort_index()
    #     df = df.reset_index()
    #
    #     fig_order = px.scatter(
    #         df,
    #         x="Datetime",
    #         y="price",
    #         color="ordtype",
    #         hover_data=[
    #             "ref",
    #             "status",
    #             "size",
    #             "ordtype",
    #             "price",
    #             # "kind",
    #             # "life_cycle",
    #             # "type_order",
    #             # "bar_created",
    #             # "high",
    #             # "low",
    #         ],
    #         category_orders={"ordtype": ["Buy", "Sell"]},
    #     )
    #
    #     long_color = "#a85f42"
    #     short_color = "#1d6f8c"
    #
    #     fig_order.data[0].marker.symbol = 22
    #     fig_order.data[0].marker.size = 8
    #     fig_order.data[0].marker.color = long_color
    #     fig_order.data[0].marker.opacity = 0.75
    #
    #     fig_order.data[1].marker.symbol = 22
    #     fig_order.data[1].marker.size = 8
    #     fig_order.data[1].marker.color = short_color
    #     fig_order.data[1].marker.opacity = 0.75
    #
    #     # fig.append_trace(fig_order.data[0], row=1, col=1)
    #     # fig.append_trace(fig_order.data[1], row=1, col=1)
    #
    #     return fig_order

    def volume(self, df=None):
        if df is None:
            df = self.dfs["ohlcv"]
        df = df.reset_index()
        fig = px.bar(df, x=df["Datetime"], y=df["Volume"].values)
        fig.data[0].marker.color = "blue"
        return fig

    def cash_value(self, df=None):
        if df is None:
            df = self.dfs["value"]
        df = df.reset_index()

        y_min = df[["Cash", "Value"]].min().min()
        y_max = df[["Cash", "Value"]].max().max()

        df = df.sort_values('Datetime')
        fig = px.line(df, x=df["Datetime"], y=df["Value"].values, )
        fig.data[0].line.color = "green"

        return fig


    def create_test_plot(self):

        fig = self.ohlc()
        # fig = self.trade_list( )
        ### fig = self.order_history()
        # fig = self.volume()
        # fig = self.cash_value()

        # return fig
        return fig.update_layout(self.set_layout())

if __name__ == "__main__":
    btplot = backtest_plot()
    plotly.offline.plot(btplot.create_test_plot())

