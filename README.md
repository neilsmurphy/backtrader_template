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

# Installation
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

















The standard setup will run a backtest on the ES Mini from `2020-06-01` on the `ES
Mini`. This test will run on minute data and last for 10 days. The test will use a
moving average as a signal to enter and use a custom stop order strategy to exit.
This custom strategy results in orders being changed nearly every bar.

Initially the backtest will print out the parameters in use for this test at the top
of the terminal.

A printout will go to terminal with orders, transactions, and final trades list. The
final value will also be shown.

Also in the '''backtest_results''' directory a spreadsheet with test results is saved.


### Running the backtests
The first section of the backtest contains:

- print_params: This will print out all the parameters that will be used in the backtests, including those that are
  defaults and not visible. Additionally shows the lists of inputs for each parameter if it exists.
- run_tests_now: Allows turning on/off the actual running of the backtests.
- multi_pro: Determines if the multi-processor gets used. True to use multi-processing, false to run each backtest one
  at a time.
- reset_database: Used to delete all data in the database before running a backtest. If True, all the tables will be
  deleted from the database provide a clean slate for the backtest results. You will be prompted to confirm the deletion.
  If false, the data in the database is left as is and the backtest result can be added to the database which allows for
  access to the current and older backtests in the dashboard at the same time.

## Configuration
| Input       | Description |
| ----------- | ----------- |
|data_path|Data filepath including directory. (string)|
|save_result|Backtest results save to excel or database. (True/False)|
|save_agg|Save backtest results to the aggregate spreadsheet. (True/False)|
|save_excel|Save detailed backtest results to a spreadsheet. (True/False)|
|save_db|Save backtest results to the database for use with dashboard. (True/False)|
|save_path|Name of the directory to save results to. (string)|
|save_name|Name of the file/database to save results to. (string)|
|---------------------|
|from_date|Date data starts loading from. Format "YYYY-MM-DD" (string)|
|trade_start|Date trading starts from. Format "YYYY-MM-DD" (string)|
|to_date|End date. Format "YYYY-MM-DD" (string)|
|---------------------|
|instrument|Name of the security. (string)|
|initinvestment|Amount of the initial investment. (float)|
|commission|Commission per contract (float)|
|margin|Amount of dollar margin per contract. Must be at least 1 for commission to be dollar/contract. (float)|
|mult|Multiplier used for calculating pnl for futures contracts (integer)|
|---------------------|
|print_dev|Developer terminal output. Can comment/uncomment lines in extension.strategy print_dev (True/False)|
|print_orders_trades|Terminal output for orders. (True/False)|
|printon|Terminal output for beginning/end details. (True/False)|
|print_ohlcv|Terminal output for ohlcv. (True/False)|
|print_final_output|Terminal output for final trade list results. (True/False)|
|---------------------|
|care_about_session_times|Restrict trading hours. (True/False)|
|rth_start|Start of regular trading. Format "YYYY-MM-DD" (string)|
|rth_end|End of regular trading. Format "YYYY-MM-DD" (string)|
|lh_start|Start of lunch hour. Format "YYYY-MM-DD" (string)|
|lh_end|End of lunch hour. Format "YYYY-MM-DD" (string)|
|rth_last_trade_time|Latest time a trade may be entered during RTH. Format "YYYY-MM-DD" (string)|
|rth_close_trade_time|Close all trades at this time. Format "YYYY-MM-DD" (string)|
|xth_start|Start extended trade session. Format "YYYY-MM-DD" (string)|
|xth_end|End extended trade session. Format "YYYY-MM-DD" (string)|
|xth_last_trade_time|Last time a trade may be entered during extended trade session. Format "YYYY-MM-DD" (string)|
|---------------------|
|gma_on|Global trend on or off. (True/False)|
|gema|text|
|gma_period_fas|text|
|gma_period_slow|text|
|---------------------|
|h1_take_profit|h1 take profit level (float)|
|h2_size|h2 trade size (integer)|
|h2_take_profit|h2 take profit level (float)|
|h3_size|h3 trade size (integer)|
|h3_take_profit|h3 take profit level (float)|
|---------------------|
|tr_on|	TRUE|	Trailing orders system, toggle on/off.|
|tr_stop_trail_builtin|	FALSE|	Use the standard stop trail built into Backtrader. |
|tr_stop_offset|	0|.5	Trailing stop order offset.|
|tr_trail_system|	dynamic|	Set which trailing stop system to use. Regular bars, EMA, or Dynamic. |
|tr_trail_max|	3|	Maximum offset for the Dynamic system. |
|tr_trail_min|	0.5|	Minimum offset for the Dynamic system. |
|tr_trail_target_bars|	28|	The projected/estimated bar period for a ideal trade to complete. |
|tr_dynamic_max|	31|	Maximum number for bars to use to calculate the inital moving average for the dynamic trailing system. |
|tr_dynamic_min|	15|	Minimum number for bars to use to calculate the final moving average for the dynamic trailing system. |
|tr_profit_target|	5|	Estimate profit per trade used to detrmine how fast to accelerate the dynamic moving average when creating trailing orders. |



To run multiple backtest simply use an iterable. 

Examples:
```
instrument=["F", "TSLA", "AAPL", "FB", "V", "BAC"],
sma_fast=list(range(15, 61, 15)),
```
If you want to try different dates, it's a bit tricky. You can use a start date and 
change the duration using a list. If you want multiple start and end dates, then 
this needs to be handled outside the params dictionary. Let me know if you need this. 
I have some sample code. 

The system will automatically calculate all of the possible combinations. The output 
will tell you how many test will run. If you want to just check how many 
test will run, set `run_test_now = False` and run the backtests. It won't actually 
run, just give you the parameters and number of test that will execute. 

To run multi processor, use: `multi_pro = True`

If you are setting up lists that will have overlap in your back testing, you can set 
some criteria to eliminate overlapping tests. For example suppose you have two sma's as 
follows 

```
sma_fast=list(range(15, 61, 15)),
sma_slow=list(range(30, 91, 15)),
```

Clearly there is some overlap where the fast is slower than the slow. In the 
RunBacktest class in the `scenario` method line 454 you can add in the following to 
skip these backtests: 

```
if scenario["sma_fast"] >= scenario["sma_slow"]:
    continue
```

To add a new parameter to the backtest, just add it into the RunBacktest class. This 
will then become available in the strat as a parameter. For example, I will add in 
your name 'Chewbacca'.

You can see it as a print out when we run the back test. 

You will notice I'm using a dictionary with two parameters at the entry point to 
runbacktest. The second parameter is boolean and is used to determine if this 
parameter is exported to the database after running the backtest for use for 
whatever, usually to identify which backtest is which. 

In the setup file, you can select different save settings and print settings. Again 
these are all explained in the RunBacktest doc strings. 

A discussion about memory. I try to separate analyzers into two cataegories. Those
that essentially have one line output per test, and analyzers that have multiple lines 
per test. If I'm only executing a modest number of backtests, I will go ahead and use a 
'full_export' to the database, meaning all analyzers. But saving OHLV data and other 
such large datasets is not conducive to large backtest. For large backtests I will set 
'full_export=False' which is good for fast backtesting. You can control which analyzers 
are included in full or not full in the extension/analyzer module at the bottom. 

On the topic of extensions I try to split out all of my specific task classes in 
separate modules in the extension directory and then import to main as needed. I find 
this keeps things tidy. Also I would normally put in sizer and any other modules in 
extension. 

You will notice as well I have a strategy class in extension. I use this for 
standard strategy stuff and then use this as a base class in the main Strategy class 
in the main module. 

Database information is in the .env file. I'm using postgres via SQLAlchemy. You can 
adjust the database settings in the utils.py file. 

You can have a backtest export to excel using 'save_excel=True' Set the directory 
and filename using: 

```
save_path="your_save_path",
save_name="your_file_name",
```
