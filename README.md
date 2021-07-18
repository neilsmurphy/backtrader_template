
[![GitHub issues:](https://img.shields.io/github/issues/neilsmurphy/backtrader_template)](https://github.com/neilsmurphy/backtrader_template/issues)
[![GitHub stars:](https://img.shields.io/github/stars/neilsmurphy/backtrader_template)](https://github.com/neilsmurphy/backtrader_template/stargazers)
[![GitHub license:](https://img.shields.io/github/license/neilsmurphy/backtrader_template)](https://github.com/neilsmurphy/backtrader_template/blob/master/LICENSE)
![Style:](https://img.shields.io/badge/code%20style-black-black)

# Backtrader Template
Backtrader Template creates new environments for onboarding clients at 
RunBacktest. The benefits of working with Backtrader Template are: 
- Easy management of parameters in a setup file.
- Easy ability to run multiple test for optimization using multi-processing.
- Simple to change outputs to terminal. 
- Easy integration of analyzers and indicators.
- Standard outputs available: 
    - Terminal
    - Excel spreadsheets
    - Database
    - Tearsheets
- Single backtest details analysis in Jupyter.
- Multi-backtest analysis in Jupyter.

## Installation
Follow these steps to install and run a basic backtest.
1. Clone the repo to your local machine.
    - HTTPS: ```git clone https://github.com/neilsmurphy/backtrader_template.
      git```
      Then enter your user name and password.
    - SSH: ```git@github.com:neilsmurphy/backtrader_template.git```
2. Create a virtual environment in the main repo directory.
   ```
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Run a backtest with standard settings.
   ```
   python3 setup.py
   ```

## Setup
The key file for interfacing with Backtrader Template is the setup.py file. Here you 
will set your parameters for your backtests.  

The first section of the backtest contains:  

- print_params: This will print out all the parameters that will be used in the 
  backtests, including those that are defaults and not visible. Additionally shows the 
  lists of inputs for each parameter if it exists.
- run_tests_now: Allows turning on/off the actual running of the backtests. Useful 
  if you just want to view the parameters before running tests. 
- multi_pro: Determines if the multi-processor gets used. True to use multi-processing, 
  false to run each backtest one at a time.
- reset_database: Used to delete all data in the database before running a backtest. 
  If True, all the tables will be deleted from the database provide a clean slate for 
  the backtest results. You will be prompted to confirm the deletion. If false, the 
  data in the database is left as-is and the backtest result can be added to the 
  database which allows for access to the current and older backtests.


#### Individual test parameters.
| Input       | Description |
| ----------- | ----------- |  
|batchname|Name to identify multiple backtests together. (string)|  
|from_date|Date data starts loading from. Format "YYYY-MM-DD" (string)|  
|trade_start|Date trading starts from. Format "YYYY-MM-DD" (string)|  
|to_date|End date. Format "YYYY-MM-DD" (string)|  
|duration|Combined with start date. Used in multiple backtests. `to_date` must be off. (int)|  
|---------------------|
|initinvestment|Amount of the initial investment. (float)|
|instrument|Name of the security. (string)|
|benchmark|Used in the tearsheet to compare against test results. (string)|
|---------------------|
|sma_fast|Simple moving average fast (int)|
|sma_slow|Simple moving average slow (int)|
|limit_price|Take profit (float)|
|stop_price|Stop loss (float)|
|---------------------|
|print_dev|Developer terminal output. Can comment/uncomment lines in extension.strategy print_dev (True/False)|
|print_orders_trades|Terminal output for orders. (True/False)|
|print_ohlcv|Terminal output for ohlcv. (True/False)|
|print_final_output|Terminal output for final trade list results. (True/False)|
|printon|Terminal output for beginning/end details. (True/False)|
|---------------------|
|save_path|Name of the directory to save results to. (string)|
|save_name|Name of the file/database to save results to. (string)|
|save_result|Backtest results save to excel, tearsheet, or database. False is terminal only. (True/False)|
|save_excel|Save detailed backtest results to a spreadsheet. (True/False)|
|save_tearsheet|Save quanstats tearsheet to `results`. (True/False)|
|save_db|Save backtest results to the database for use with analysis. (True/False)|
|full_export|Full export exports all of the available date. (True/False)|

#### Running backtests
All stock data is downloaded using yahoo finance. Time frames are daily. 

A simple indicator is used in this backtests. Of course this would be replaced with 
the users indicators. 

When setting dates, the `from_date` is when data is loaded, and `trade_start` is 
when trading starts. While Backtrader will automatically adjust lead times, this 
gives more control of the actual trade start date. 

`print_dev` is used for custom logging. You can change this in `extension/strategy.py`.

Multiple backtest can be run for optimization. All that is required is to use list 
where your parameters would be. 

For example, run the following tests: 
```
...
instrument= ["FB", "TSLA", "AAPL"],
benchmark="SPY",
sma_fast=range(15, 46, 15),
sma_slow=range(30, 61, 15),
limit_price=[0.04, 0.07, 0.09],
stop_price=[0.02, 0.05],
...
```
This will run the following tests. 
```

There will be 108 backtests run.

    batchname="Single Test",
    batch_runtime="2021-06-20 06:52",
    db_name=None,
    test_number=0,
    save_result=True,
    save_tearsheet=True,
    save_excel=True,
    save_db=False,
    full_export=True,
    save_path="result",
    save_name="my test name",
    from_date="2016-01-01",
    trade_start="2016-09-01",
    to_date="2020-12-31",
    duration=None,
    instrument=['FB', 'TSLA', 'AAPL'],
    benchmark="SPY",
    initinvestment=100000,
    commission=0.0,
    margin=None,
    mult=1,
    print_dev=False,
    print_orders_trades=True,
    printon=True,
    print_ohlcv=-1,
    print_final_output=True,
    ploton=False,
    sma_fast=range(15, 46, 15),
    sma_slow=range(30, 61, 15),
    limit_price=[0.04, 0.07, 0.09],
    stop_price=[0.02, 0.05],
    trade_size=1.0,
```
The system will automatically calculate all of the possible combinations. The output
will tell you how many test will run. If you want to just check how many
test will run, set `run_test_now = False` and run the backtests. It won't actually
run, just give you the parameters and number of test that will execute. 
Criteria is set in the calculation of the backtest to ensure that the long sma is 
higher than the short sma. This logic can be found in `main/RunBacktest/scenario` at 
line 457. 
```
if scenario["sma_fast"] >= scenario["sma_slow"]:
    continue
```
When running multiple backtest, make sure to use `multi-pro = True` to turn on the 
multi-processor. The multi-processor is set to use your `number of cores - 2`. 

To run multiple test at once over different dates, use the `from_date` combined with 
`duration`. `trade_start` and `to_date` are ignored. 

#### Backtest results
View your backtest results on the terminal, save to excel, database, or create a 
tearsheet. 

##### Terminal
There are several options for diplaying backtest results to the terminal. 
To view all orders and trades, `print_orders_trades`. 
One can also select to view all of the ohlcv candles using `print_ohlcv=0`. If there 
are more than one data lines in the backtest, select increasing increments, eg: 
`print_ohlcv=1` to find the desired dataline. Use `-1` for off. 
Backtrader template offers a trade output list which can be accessed via 
`print_final_output=True` [Thanks to https://github.com/ab-trader]
There are some sundry printouts such as the final value, etc. `printon=True`
Also is available the ability to create a custom log to terminal using 
'print_dev=False,' This can be modified in `extensions/strategy.py`.

##### To disk
There are three options for saving to disk. To turn on/off saving in general, use 
`save_result=False`. To set the path for saving, `save_path="result"` This will 
save to the "result" directory. It is not necessary to create the directory, it will 
be made if not already existing. A custom name can be added to the output file names.
`save_name="my test name"`.
To save to excel, use `save_excel=True`. The spreadsheet will have multple tabs with 
the following information: 
- trade_list: Summary of all trades. 
- trade_analysis: Backtraders detailed backtest [TradeAnalysis](https://www.backtrader.com/docu/analyzers-reference/#tradeanalyzer). 
- drawdown: Overall drawdown stats.
- transaction: Each transaction, including partial fills. 
- value: Cash and market value at each bar. 
- trade: Backtrader's trade summary. 
- ohlcv: Stock OHLCV bars. 
- benchmark: Benchmark OHLCV bars.
- dimension: These are the input parameters and other settings for the backtest. 

The above data can also be saved to database using `save_db=True` This is necessary 
for analysis. This default template uses SQLite3 for simplicity, but any database 
could be used. I personally use postgres. 

There is a very nice tearsheet provided by [QuantStats](https://github.com/ranaroussi/quantstats). This can be accessed by using `save_tearsheet=True`. 
Here is a sample: ![Tearsheet](https://github.com/neilsmurphy/backtrader_template/blob/main/result/my%20test%20name-Single%20Test-20210620_0802.jpg)

##### Memory
A discussion about memory. I try to separate analyzers into two categories. Those
that essentially have one line output per test, and analyzers that have multiple lines
per test. If I'm only executing a modest number of backtests, I will go ahead and use a
'full_export' to the database, meaning all analyzers. But saving OHLV data and other
such large datasets is not conducive to large numbers of backtests. For large 
backtests I will set
'full_export=False' which is good for fast backtesting. You can control which analyzers
are included in full or not full in the extension/analyzer module at the bottom. 

#### Analysis
There are two analysis notebooks. 
1. single_analysis.ipynb
   Used to provide a detailed analysis for a single backtest. The charts are the 
   same as contained in the tearsheet. 
2. analysis.ipynb
   Used for comparing multiple spreadsheets across parameters primarily using 
   heatmaps. 

#### Create new parameters
To add a new parameter to the backtest, just add it into the RunBacktest class 
`self.params` dictionary found in `main.py`. The default for the parameter is placed in the 
first position of the list. This will then become available in the strat as a 
parameter. For example, adding in `rsi` as a true/false parameter: 

```rsi=[True, True],```

This parameter is now availabe in your backtest in the strategy by using 
``` 
self.p.rsi
```

The second parameter is boolean and is used to determine if this 
parameter is exported to the database after running the backtest for use in analysis. 


#### Extensions
Separate modules are stored in the extension directory and then import to main as 
needed. Modules that are stored here are: 
- analyzer: For gathering information on test results. 
- indicator: Creates signals for trading. 
- result: For generating spreadsheets and database outputs. 
- sizer: Can be used for sizing trades. (Not used in default settings.)
- strategy: Superclass for strategy with standard methods.



## CCXT and crypto currencies
Now encorporated is Dave Valance/Ed Bartosh ccxt stores into backtrader. You can now 
backtest cryptos on a wide variety of exchanges. Once backtested, you can sandbox test 
your algo, then go live. 

The sample included is Binance. Set up your parameters as per the `params-template.json` 
file. 

| WARNING Do not mix up your testnet and your live trading. `Testnet` is a fake sandbox account trading pretend money, `actual` trading is live with your money.   |
|-----------------------------------------|

I have set up two apis, one for actual trading and one for the testnet sandbox. 
```python
 "binance_actual": {
    "apikey": "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "secret": "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "testorders": true
  },

  "binance_testnet": {
    "apikey": "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "secret": "~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~",
    "testorders": true
  },
```

Create your configs for your store. For the testnet use: 
```python
config = {'urls': {'api': 'https://testnet.binance.vision/api'},
          "apiKey": params["binance_testnet"]["apikey"],
          "secret": params["binance_testnet"]["secret"],
          "enableRateLimit": True,
          }
```

For your actual store with live trading, use: 
```python
config = {
    "apiKey": params["binance_actual"]["apikey"],
    "secret": params["binance_actual"]["secret"],
    "enableRateLimit": True,
}
```
When trading on the sandbox, set `sandbox=True` when creating the store. And `sandbox=False` 
when trading live. 
```python
store = CCXTStore(
    exchange="binance", currency="USDT", config=config, retries=5, debug=False, sandbox=True
)
```
## Dependencies  
Packages required:   
[Black](https://github.com/psf/black)  
[Dash Bootstrap Components](https://dash-bootstrap-components.opensource.faculty.ai)  
[Jupyter](https://jupyter.org)  
[Quandl](https://github.com/quandl/quandl-python)    
[Pandas](https://github.com/pandas-dev/pandas)  
[Plot.ly](https://plotly.com/python/)  
[Plot.ly Dasy](https://plotly.com/dash/)  
[tabulate](https://github.com/astanin/python-tabulate)  
[urllib3](https://urllib3.readthedocs.io)  
[XlsxWriter](https://github.com/jmcnamara/XlsxWriter)  
[Yfinance](https://github.com/ranaroussi/yfinance)  
## License
[MIT](https://github.com/neilsmurphy/backtrader_template/blob/master/LICENSE)  

## Contact
If you wish to contact me, I can be reached: 

Neil Murphy  
neil@runbacktest.com  
[RunBacktest](https://runbacktest.com)  
