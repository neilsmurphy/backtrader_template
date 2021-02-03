Chewbacca, 

I've added this to a private github and cleaned up my documentation. Please keep 
this private for now. I would appreciate any feedback. 

This readme file was done quickly so please forgive the sloppiness. 

### Notes

Set up a virtual environment using the `requirements.txt` file. 

Set up backtests using the setup.py file. 

For instructions on parameters see the docstring in the class RunBacktest in main.py.

To run multiple backtest simply use an iterable. 

Examples:
instrument=["F", "TSLA", "AAPL", "FB", "V", "BAC"],
sma_fast=list(range(15, 61, 15)),

If you want to try different dates, it's a bit tricky. You can use a start date and 
change the duration using a list. If you want multiple start and end states, then 
this needs to be handled outside the params dictionary. Let me know if you need this 
I have some sample code. 

The system will automatically calculate all of the possible combinations. The output 
will tell you how many test will run. If you want to just check how many 
test will run, set `run_test_now = False` and run the backtests. It won't actually 
run, just give you the parameters and number of test that will execute. 

To run multi processor, use: `multi_pro = True`

If you are setting up list that will have overlap in your back testing, you can set 
some criteria to eliminate those ones. For example suppose you have two sma's as 
follows 

```
sma_fast=list(range(15, 61, 15)),
sma_slow=list(range(30, 91, 15)),
```

Clearly there is some overlap where the fast is slower than the slow. In the 
RunBacktest class in the `scenario` method line 454 you can add in the following: 

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
extension. You will notice as well I have a strategy class in extension. I use this  
for standard strawtegy stuff and then use this as a base class in the main Strategy  
class in the main module. 

Database information is in the .env file. I'm using postgres. You can have a 
backtest export to excel using 'save_excel=True'

Hope this helps. Again pleae keep private for now. I will likely publish all of this 
in the next month or so, just too busy right now. 