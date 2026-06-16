import os
from datetime import datetime

from xlsxwriter import Workbook

from social_pulse.settings import MEDIA_ROOT, MEDIA_URL


def get_styles(workbook: Workbook):
    title = workbook.add_format()
    title.set_font_name('Times New Roman')
    title.set_font_size(12)
    title.set_align('vcenter')
    title.set_bg_color('#F8F9FA')
    title.set_border()
    title.set_border_color('#BFBFBF')

    value = workbook.add_format()
    value.set_font_name('Times New Roman')
    value.set_font_size(12)
    value.set_align('center')
    value.set_align('vcenter')
    value.set_bg_color('#F8F9FA')
    value.set_border()
    value.set_border_color('#BFBFBF')
    value.set_text_wrap()

    increase = workbook.add_format()
    increase.set_font_name('Times New Roman')
    increase.set_font_size(12)
    increase.set_align('center')
    increase.set_align('vcenter')
    increase.set_color('#28A745')
    increase.set_bg_color('#F8F9FA')
    increase.set_border()
    increase.set_border_color('#BFBFBF')

    decrease = workbook.add_format()
    decrease.set_font_name('Times New Roman')
    decrease.set_font_size(12)
    decrease.set_align('center')
    decrease.set_align('vcenter')
    decrease.set_color('#DC3545')
    decrease.set_bg_color('#F8F9FA')
    decrease.set_border()
    decrease.set_border_color('#BFBFBF')

    return title, value, increase, decrease


def insert_header(sheet, value, group_count):
    if group_count >= 6:
        sheet.merge_range('D1:J1', f'Сравнительный отчет по группам. Количество групп: {group_count}', value)
    else:
        sheet.merge_range('A1:E1', f'Сравнительный отчет по группам. Количество групп: {group_count}', value)


def insert_table_header(sheet, value, row=1):
    header_data = ('Платформа', 'Дата добавления', 'Подписчики', 'Лайки', 'Комментарии',
                   'Просмотры', 'Репосты', 'Кол-во постов', 'Прирост за неделю')
    start = 5
    if row == 1:
        sheet.merge_range('A3:A4', 'Признак/название', value)
    elif row == 2:
        sheet.merge_range('A18:A19', 'Признак/название', value)
        start = 20

    for cell_nmb, data in enumerate(header_data, start=start):
        sheet.write(f'A{cell_nmb}', data, value)


def insert_data_row(sheet, value, increase_style, decrease_style, data, row=1):
    for idx, cell in enumerate(range(1, len(data) * 2 + 1, 2)):
        name = data[idx].get('name')
        if len(name) > 25:
            name = f'{name[:20]}...'
        platform = data[idx].get('platform').get('alias')
        added_at = data[idx].get('added_at')
        date = datetime.fromisoformat(added_at).strftime('%d.%m.%Y')

        participants = data[idx].get('abs_stats').get('participants_count')
        likes = data[idx].get('abs_stats').get('likes_count')
        comms = data[idx].get('abs_stats').get('comms_count')
        views = data[idx].get('abs_stats').get('views_count')
        reposts = data[idx].get('abs_stats').get('repost_count')
        posts = data[idx].get('abs_stats').get('posts_count')
        increase = data[idx].get('increase')
        if increase > 0:
            increase = f'+{str(increase)}'
            style = increase_style
        elif increase < 0:
            style = decrease_style
        else:
            style = value

        if row == 1:
            sheet.merge_range(2, cell, 3, cell + 1, name, value)
            sheet.merge_range(4, cell, 4, cell + 1, platform, value)
            sheet.merge_range(5, cell, 5, cell + 1, date, value)
            sheet.merge_range(6, cell, 6, cell + 1, participants, value)
            sheet.merge_range(7, cell, 7, cell + 1, likes, value)
            sheet.merge_range(8, cell, 8, cell + 1, comms, value)
            sheet.merge_range(9, cell, 9, cell + 1, views, value)
            sheet.merge_range(10, cell, 10, cell + 1, reposts, value)
            sheet.merge_range(11, cell, 11, cell + 1, posts, value)
            sheet.merge_range(12, cell, 12, cell + 1, increase, style)
        else:
            sheet.merge_range(17, cell, 18, cell + 1, name, value)
            sheet.merge_range(19, cell, 19, cell + 1, platform, value)
            sheet.merge_range(20, cell, 20, cell + 1, date, value)
            sheet.merge_range(21, cell, 21, cell + 1, participants, value)
            sheet.merge_range(22, cell, 22, cell + 1, likes, value)
            sheet.merge_range(23, cell, 23, cell + 1, comms, value)
            sheet.merge_range(24, cell, 24, cell + 1, views, value)
            sheet.merge_range(25, cell, 25, cell + 1, reposts, value)
            sheet.merge_range(26, cell, 26, cell + 1, posts, value)
            sheet.merge_range(27, cell, 27, cell + 1, increase, style)



def generate_comparative_report_excel(compare_result):
    filename = f"Сравнительный_отчет_{datetime.now().strftime('%d.%m.%Y_%H%M%S')}.xlsx"
    xlsx_path = os.path.join(MEDIA_ROOT, 'reports', 'xlsx', 'comparative')
    os.makedirs(xlsx_path, exist_ok=True)
    filepath = os.path.join(xlsx_path, filename)
    relative_path = os.path.join(MEDIA_URL, 'reports', 'xlsx', 'comparative', filename).replace('\\', '/')
    workbook = Workbook(filepath)

    report_sheet = workbook.add_worksheet('Отчет')
    report_sheet.set_landscape()
    report_sheet.set_paper(9)
    report_sheet.fit_to_pages(1, 0)

    report_sheet.set_column(0, 0, 19)
    report_sheet.set_column(1, 15, 8.43)

    title, value, increase, decrease = get_styles(workbook)

    group_count = len(compare_result)

    insert_header(report_sheet, value, group_count)
    insert_table_header(report_sheet, title)
    if group_count > 6:
        insert_table_header(report_sheet, title, 2)

    insert_data_row(report_sheet, value, increase, decrease, compare_result[:6])
    insert_data_row(report_sheet, value, increase, decrease, compare_result[6:], 2)

    workbook.close()
    return filepath, relative_path
