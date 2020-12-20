from openpyxl import Workbook
from openpyxl.worksheet.worksheet import Worksheet
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.styles import Alignment
from pandas import DataFrame


def write_results(folder_path: str, file_name: str, results: DataFrame, draw_result: dict, prize_breakdown: dict):
    workbook = Workbook()
    workbook.remove(workbook.active)  # remove default 'Sheet'

    result_sheet = workbook.create_sheet('Result', 0)
    draw_sheet = workbook.create_sheet('Draw Outcome', 1)
    prize_breakdown_sheet = workbook.create_sheet('Prize Breakdown', 2)

    for row in dataframe_to_rows(results, index=False, header=True):
        result_sheet.append(row)

    write_dict(draw_sheet, draw_result, [])
    write_dict(prize_breakdown_sheet, prize_breakdown, ['Match Type', 'Prize Per UK Winner'])

    tidy_workbook(workbook)
    workbook.save(f'{folder_path}/{file_name}.xlsx')


def write_dict(sheet: Worksheet, data: dict, col_names: list):
    if col_names:
        sheet.append(col_names)
    for item in data.items():
        sheet.append(item)


def tidy_workbook(workbook: Workbook):
    desired_alignment = Alignment(horizontal="center", vertical="center")
    for name in workbook.sheetnames:
        sheet = workbook.get_sheet_by_name(name)
        for column_cells in sheet.columns:
            desired_length = sheet.column_dimensions[column_cells[0].column_letter].width
            for cell in column_cells:
                desired_length = max(len(as_text(cell.value)), desired_length)
                cell.alignment = desired_alignment
            sheet.column_dimensions[column_cells[0].column_letter].width = desired_length


def as_text(value):
    if value is None:
        return ""
    else:
        return str(value)
