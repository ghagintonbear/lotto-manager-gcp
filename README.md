# Lotto-Manager

Python application which automates and manages a lottery syndicate for the Euro-Millions. It has been designed to 
meet specific users needs. 

User has requested the following requirements:
* An Application to run on their Windows machine, executed via a Windows executable or equivalent.
* Information outputs to be stored in `xlsx` files.
* From Prize break down extract `Prize Per UK Winner`.
* The types of cumulative summaries produced in `./Master Results.xlsx`. e.g. Breakdown per-player which allows user
to determine how much a participant in their syndicate has earned.
* A GUI.

## Project Structure

All Python logic is stored in the `./manager/` directory. The `./manager/` directory is organised into modules which
contain the logic for performing various jobs, such as scraping information from the internet and writing the results 
to `xlsx` outputs in the appropriate directories. Majority of the functions in these modules have been unit tested
in `./tests`. See coverage below.

High level functions which run the manager are kept in `./manager/__init__.py`

Assumed python path is the lead directory.

Other Key files:
* `./Selected Numbers.xlsx` - which contains the numbers the syndicate play with.
* `./Run Manager.bat` - Executes the GUI manager.

## Running the Manager

To run the manager, first install the appropriate dependencies using either method below:

* Using Python dependency package manager [Poetry](https://python-poetry.org/) simply run `poetry install` in the 
lead directory.

* Alternatively, use `pip` to install `./requirements.txt` with the command: `pip install -r requirements.txt`.

Then to run the manager on a Windows machine simply double click the `./Run Manager.bat` file.

**Note**

bat script runs with global Python environment. If you're using a python virtual environment, tweak the bat script 
to do the same. e.g. 
  
> ```poetry run python -c "from manager import run_manager_with_gui; run_manager_with_gui()"```

## Running Tests

Unit tests have been written using `pytest`. Sometimes used in conjunction with `unittest` mock objects.

To run the tests execute `pytest` in the leading directory. 

### Testing Coverage

Coverage for `check_matches.py`, `cumulate_results.py`, `scrape_results.py`, `tools.py` in `./manager` is about 93%.
Tests for `writer.py` still need to be written.

For the functions in `gui.py` and `__init__.py` an [acceptance test document](./tests/acceptance_test_gui.md) as been
written, until integration tests are implemented.