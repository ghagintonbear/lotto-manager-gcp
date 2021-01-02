# Acceptance Tests for lotto-manager GUI

These tests can be run manually to confirm that the GUI is working as required.

To launch GUI run `./Run Manager.bat`.

**Note**

* We're using a bat file because end user is running this on a Windows machine.
* bat script runs with global python environment. If you're running this out of a python virtual environment, tweak the
  bat script to do the same.

## Test Run Day Tab

`Run Day` Tab should have:

* An interactive calendar to select run date.
* Label showing which date is selected.
* `Select Run Date` button to confirm selected new date.
* `Run Manager` button.
* `Result` Panel with a scroll bar.
* `Update Master Results` button.

### Test Steps:

1. Select a day on the calendar and confirm your choice by clicking the `Select Run Date`. This should result in the
   Label updating to show your new date in the format dd/mm/yyyy.

1. Click `Run Manager`. This should execute the `run_manager` function in `./manager/__init__.py`. If it runs
   successfully, key outcomes from run should be displayed in the `Result` panel below. This information should include:
    1. "Draw on: \<Date Selected\>"
    1. A list of the drawn numbers from the Euro-million draw on the draw date you're running on.
    1. A list of the lucky star numbers from the Euro-million draw on the draw date you're running on.
    1. File path to the where the results file has been stored.
    1. Amount won by your selected numbers.

1. If you `Run Manager` again, new result should be appended below existing.

1. Click `Update Master Results`. This should result in a yes-no prompt window asking you to confirm. If you click yes,
   this should execute `produce_cumulative_report` function in `./manager/__init__.py`. If you're running on a Windows
   machine, this should then result in the `./Master Results.xlsx` file opening with all the results from all the
   `.xlsx` files in `./results_archive`. Both new and old.

## Test Run Between Tab

`Run Between` Tab should have:

* An interactive calendar to select a date.
* Two labels showing which date is selected. One for a start date and one for an end date.
* `Select Start Date` button.
* `Select End Date` button
* `Run Manager` button.
* `Result` Panel with a scroll bar.
* `Update Master Results` button.

### Test Steps:

1. Select a day on the calendar and confirm your choice by clicking the `Select Start Date`. This should result in the
   `Start Date` Label updating to show your new date in the format dd/mm/yyyy.

1. Select a second day (after the first selected date) and confirm your choice by clicking the `Select Start Date`. This
   should result in the `End Date` Label updating to show your new date in the format dd/mm/yyyy.

1. Click `Run Manager`. This should execute the `run_manager_between` function in `./manager/__init__.py`. If it runs
   successfully, key outcomes from each friday draw between the selected start and end date run should be displayed in
   the `Result` panel below. This information should include the following for each draw:
    1. "Draw on: \<Date Selected\>"
    1. A list of the drawn numbers from the Euro-million draw on the draw date you're running on.
    1. A list of the lucky star numbers from the Euro-million draw on the draw date you're running on.
    1. File path to the where the results file has been stored.
    1. Amount won by your selected numbers.

1. You should have the ability to scroll up and down through the results in the `Result` Panel.

1. If you `Run Manager` again, new result should be appended below existing.

1. Click `Update Master Results`. This should result in a yes-no prompt window asking you to confirm. If you click yes,
   this should execute `produce_cumulative_report` function in `./manager/__init__.py`. If you're running on a Windows
   machine, this should then result in the `./Master Results.xlsx` file opening with all the results from all the
   `.xlsx` files in `./results_archive`. Both new and old.
