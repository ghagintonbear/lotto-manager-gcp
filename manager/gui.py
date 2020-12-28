import re
from datetime import datetime
from tkinter import Tk, Frame, Label, Button, Canvas, Scrollbar, LEFT, messagebox
from tkinter.ttk import Notebook
from typing import Callable

from pandas import Series
from tkcalendar import Calendar

from manager.tools import currency_to_int


def run_gui(run_day_fn: Callable, run_between_fn: Callable, cumulative_report_fn: Callable):
    """ Makes and runs GUI. """
    window = Tk()
    window.title('Euro Million Lottery Manager')
    window.geometry("550x650")
    # split window into tabs
    notebook = Notebook(window)

    run_day_frame = Frame(notebook)
    run_day_frame.configure(bg='#335C67')
    _make_run_gui(run_day_frame, run_day_fn, cumulative_report_fn)
    notebook.add(run_day_frame, text='Run Day')

    # Run between tab
    run_between_frame = Frame(notebook)
    run_between_frame.configure(bg='#335C67')
    _make_run_gui(run_between_frame, run_between_fn, cumulative_report_fn, run_between=True)
    notebook.add(run_between_frame, text='Run Between')

    notebook.pack(expand=1, fill="both")

    window.mainloop()


def _make_run_gui(frame: Frame, run_manager_fn: Callable, cumulative_report_fn: Callable, run_between: bool = False):
    """ Makes GUI for both tabs. This includes:
        * `tkcalendar`,
        * date selected Label(s) and Button(s),
        * run manager button,
        * a scrollable label to log results,
        * cumulative results button.
    """
    calendar = Calendar(frame, selectmode="day", date_format="dd/mm/yyyy")
    calendar.grid(column=0, row=0, padx=20, pady=20, columnspan=1, rowspan=10)

    Label(frame, text="Result:", font=('Calibri bold', 15)).grid(column=0, row=11, sticky='w', padx=20)
    log_label = _make_scrolling_label_log(frame)

    if run_between:
        start_date_label = _add_label_button_date_select(frame, calendar, label_text='Start Date',
                                                         label_col=1, label_row=1)
        end_date_label = _add_label_button_date_select(frame, calendar, label_text='End Date',
                                                       label_col=1, label_row=3)
        run_button = Button(frame, text="Run\nManager", font=('Calibri', 12),
                            command=lambda: run_manager_fn(_get_date_from_label(start_date_label),
                                                           _get_date_from_label(end_date_label), log_label))
    else:
        _add_label_button_date_select(frame, calendar, label_text='Run Date',
                                      label_col=1, label_row=1)
        run_button = Button(frame, text="Run\nManager", font=('Calibri', 12),
                            command=lambda: run_manager_fn(calendar.selection_get(), log_label))

    run_button.configure(bg='#E09F3E')
    run_button.grid(column=2, row=2, rowspan=3, padx=12, sticky='nesw')

    cumulative_button = Button(frame, text="Update\nMaster\nResults", font=('Calibri', 12),
                               command=lambda: _message_box_prompt(cumulative_report_fn))
    cumulative_button.configure(bg='#E09F3E')
    cumulative_button.grid(column=2, row=13, sticky='nesw', pady=10)

    return log_label


def _message_box_prompt(execute_fn: Callable[[], None], title: str = "Update Master Results",
                        message: str = 'Update "Master Results.xlsx"?'):
    """ Prompts user to confirm before executing execute_fn. Only used for Update Master Results."""
    confirm_update = messagebox.askyesno(title=title, message=message)
    if confirm_update:
        execute_fn()


def _add_label_button_date_select(frame: Frame, calendar: Calendar, label_text: str, label_row: int, label_col: int,
                                  padding: int = 1):
    """ Make generic date select Label and Button. Used over both tabs."""
    font = ('Calibri', 12)

    label = Label(frame, text=f"{label_text}: {calendar.selection_get():%d/%m/%Y}", font=font, bg='#FFF3B0')
    label.grid(column=label_col, row=label_row, pady=padding)

    button = Button(frame,
                    text=f"Select {label_text}",
                    command=lambda: _grab_date_from_calendar(label, calendar, label_text),
                    font=font, bg='#E9C46A')

    button.grid(column=label_col, row=label_row + 1, pady=padding)

    return label


def _grab_date_from_calendar(label: Label, calendar: Calendar, text: str):
    """ extract date in string format from calendar. """
    label.config(text=f"{text} selected:\n{calendar.selection_get():%d/%m/%Y}")


def _make_scrolling_label_log(frame: Frame):
    """ logic to make a scrollable label box. First you have to create a canvas and then a new frame within that canvas.
        Then add the Label within that new frame. Note, you have to bind the frame to canvas.
    """
    canvas = Canvas(frame)
    canvas.grid(column=0, row=12, columnspan=3, padx=20, pady=0, sticky='nesw')
    scrollbar = Scrollbar(frame, orient="vertical", command=canvas.yview)
    scrollbar.grid(column=0, row=12, columnspan=3, sticky='nes')
    scrollable_frame = Frame(canvas)
    scrollable_frame.configure(bg='#FFF3B0')

    scrollable_frame.bind(
        "<Configure>",
        lambda e: canvas.configure(
            scrollregion=canvas.bbox("all")
        )
    )

    canvas.create_window((0, 12), window=scrollable_frame, anchor="nw")

    canvas.configure(yscrollcommand=scrollbar.set, bg='#FFF3B0')

    log_label = Label(scrollable_frame, text="", anchor='w', justify=LEFT, bg='#FFF3B0')
    log_label.grid(column=0, row=12, columnspan=2, padx=20, pady=0, sticky='nesw')

    return log_label


def _get_date_from_label(label: Label):
    """ extracts date from label text using regex"""
    return datetime.strptime(re.search(r'(\d{2}/\d{2}/\d{4})', label.cget('text'))[0], '%d/%m/%Y').date()


def update_label_log(label: Label, draw_date: str, winning_numbers: dict, folder_path: str, prize_col: Series):
    """ updates label with given information in a readable format. """
    prize_sum = currency_to_int(prize_col).sum() / 100
    result = "\n\n    -".join([
        'Euro-Million Draw On: ' + draw_date,
        f'Draw Numbers: {winning_numbers["Balls"]}',
        f'Lucky Stars: {winning_numbers["Lucky Stars"]}',
        f'Results for this draw stored in: {folder_path}',
        f'You have won: £{prize_sum:.2f}'
    ])

    current = label.cget("text")
    label.config(text=current + "\n\n" + result if current else result)
