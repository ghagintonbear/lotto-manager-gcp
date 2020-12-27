from tkinter import Tk, Frame, Label, Button
from tkinter.ttk import Notebook
from tkcalendar import Calendar


def run_gui(run_day_fn, run_between_fn):
    window = Tk()
    window.title('Euro Million Lottery Manager')
    window.geometry("600x650")
    # split window into tabs
    notebook = Notebook(window)

    run_day_frame = Frame(notebook)
    run_day_log_label = make_run_day_gui(run_day_frame, run_day_fn)
    notebook.add(run_day_frame, text='Run Day')

    # Run between tab
    run_between_frame = Frame(notebook)
    run_between_log_label = make_run_between_gui(run_between_frame, run_between_fn)
    notebook.add(run_between_frame, text='Run Between')

    notebook.pack(expand=1, fill="both")

    window.mainloop()

    return run_day_log_label, run_between_log_label


def make_run_between_gui(frame, run_manager_fn):
    calendar = Calendar(frame, selectmode="day", date_format="dd/mm/yyyy")
    calendar.grid(column=0, row=0, padx=20, pady=20, columnspan=1, rowspan=10)

    _add_label_button_date_select(frame, calendar, label_text='Start Date', label_col=1, label_row=1, padding=1)
    _add_label_button_date_select(frame, calendar, label_text='End Date', label_col=1, label_row=3, padding=1)

    Button(frame, text="Run\nManager", font=('Calibri', 12), command=run_manager_fn)\
        .grid(column=2, row=2, rowspan=3, padx=12, sticky='nesw')

    Label(frame, text="Result:", font=('Calibri bold', 15)).grid(column=0, row=11)
    log_label = Label(frame, text=f"{'Test'*20}\n"*99)
    log_label.grid(column=0, row=12, padx=20, pady=0, columnspan=2)

    return log_label


def make_run_day_gui(frame, run_manager_fn):
    calendar = Calendar(frame, selectmode="day", date_format="dd/mm/yyyy")
    calendar.grid(column=0, row=0, padx=20, pady=20, columnspan=1, rowspan=10)

    _add_label_button_date_select(frame, calendar, label_text='Run Date', label_col=1, label_row=1)

    Button(frame, text="Run\nManager", font=('Calibri', 12), command=run_manager_fn)\
        .grid(column=2, row=2, rowspan=3, padx=12, sticky='nesw')

    Label(frame, text="Result:", font=('Calibri bold', 15)).grid(column=0, row=11)
    log_label = Label(frame, text=f"{'Test'*20}\n"*99)
    log_label.grid(column=0, row=12, padx=20, pady=0, columnspan=2)

    return log_label


def _add_label_button_date_select(frame, calendar, label_text, label_row, label_col, padding=0):
    font = ('Calibri', 12)

    label = Label(frame, text=f"{label_text}: {calendar.selection_get():%d/%m/%Y}", font=font)
    label.grid(column=label_col, row=label_row, pady=padding)

    button = Button(frame,
                    text=f"Select {label_text}",
                    command=lambda: _grab_date(label, calendar),
                    font=font)

    button.grid(column=label_col, row=label_row + 1, pady=padding)


def _grab_date(label, calendar):
    label.config(text=f"Date selected: {calendar.selection_get():%d/%m/%Y}")


if __name__ == '__main__':
    run_day_log_label, run_between_log_label = run_gui(run_day_fn=lambda: None, run_between_fn=lambda: None)
