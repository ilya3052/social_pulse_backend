import math
import os
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from icecream import ic
from xlsxwriter import Workbook

from reports.utils.shared_report_utils import convert_xlsx_to_pdf, sanitize
from social_pulse.settings import MEDIA_ROOT, MEDIA_URL


def _truncate_text(text, max_len=150):
    if not text:
        return 'В записи отсутствует текст.'
    if len(text) >= max_len:
        return text[:max_len - 3] + '...'
    return text


def _parse_timestamp(stat, key='timestamp'):
    _time = datetime.fromisoformat(stat.get(key).replace('Z', '+00:00'))
    return _time.astimezone(ZoneInfo('Europe/Moscow'))


def make_intervals(interval_values):
    interval_values = list(map(int, interval_values))
    start = 0
    intervals = []
    for value in interval_values:
        intervals.append(f'{start}-{value}')
        start = value
    return intervals


def get_styles(workbook: Workbook):
    value = workbook.add_format()
    value.set_font_name('Times New Roman')
    value.set_font_size(14)
    value.set_align('center')
    value.set_align('vcenter')
    value.set_bg_color('#F8F9FA')
    value.set_border()
    value.set_border_color('#BFBFBF')

    post_text = workbook.add_format()
    post_text.set_font_name('Times New Roman')
    post_text.set_font_size(12)
    post_text.set_indent(1)
    post_text.set_align('left')
    post_text.set_align('vcenter')
    post_text.set_bg_color('#F8F9FA')
    post_text.set_border()
    post_text.set_border_color('#BFBFBF')
    post_text.set_text_wrap()

    mute = workbook.add_format()
    mute.set_font_name('Times New Roman')
    mute.set_font_size(12)
    mute.set_align('center')
    mute.set_align('vcenter')
    mute.set_bg_color('#F8F9FA')
    mute.set_border()
    mute.set_border_color('#BFBFBF')
    mute.set_text_wrap()

    return value, post_text, mute


def insert_group_report_header(report_sheet, header_info, value_format):
    column_width = 8.43
    group_name = header_info.get('group_name', 'Unknown')
    group_name_width = len(group_name) * 1.2
    cols_needed = math.ceil(group_name_width / column_width)
    start_col = 0
    end_col = start_col + cols_needed - 1

    report_sheet.merge_range(0, start_col, 0, end_col, 'Название', value_format)
    report_sheet.merge_range(1, start_col, 1, end_col, group_name, value_format)
    report_sheet.merge_range(0, end_col + 2, 0, end_col + 3, 'Платформа', value_format)
    report_sheet.merge_range(1, end_col + 2, 1, end_col + 3, header_info.get('platform', 'Не указана'), value_format)
    report_sheet.merge_range('A4:F4', f'Дата формирования: {datetime.now().strftime('%d.%m.%Y')}', value_format)


def insert_group_stats(report_sheet, stats_info, value_format):
    report_sheet.merge_range('F6:I6', 'Статистика', value_format)

    report_sheet.merge_range('A8:B8', 'Посты', value_format)
    report_sheet.merge_range('A9:B10', stats_info.get('posts_count', 0), value_format)

    report_sheet.merge_range('D8:E8', 'Подписчики', value_format)
    report_sheet.merge_range('D9:E10', stats_info.get('participants_count', 0), value_format)

    report_sheet.merge_range('G8:H8', 'Лайки', value_format)
    report_sheet.merge_range('G9:H10', stats_info.get('likes_count', 0), value_format)

    report_sheet.merge_range('J8:K8', 'Репосты', value_format)
    report_sheet.merge_range('J9:K10', stats_info.get('repost_count', 0), value_format)

    report_sheet.merge_range('M8:N8', 'Комментарии', value_format)
    report_sheet.merge_range('M9:N10', stats_info.get('comms_count', 0), value_format)


def insert_aggregated_data_graphic_section(workbook, report_sheet, data_sheet, aggregated_post_data, graphic_name, cell,
                                           x_axis_name, data_rows):
    keys = make_intervals(aggregated_post_data.keys())
    values = [aggregated_post_data[item].get('count') for item in aggregated_post_data]

    data_len = len(values)

    data_sheet.write_column(f'{data_rows[0]}1', keys)
    data_sheet.write_column(f'{data_rows[1]}1', values)

    chart = workbook.add_chart({"type": "column"})
    chart.set_title({'name': graphic_name})
    chart.add_series({
        'categories': f'=Данные!${data_rows[0]}$1:${data_rows[0]}${data_len}',
        'values': f'=Данные!${data_rows[1]}$1:${data_rows[1]}${data_len}',
    })
    chart.set_y_axis({'log_base': 10, 'name': 'Количество постов'})
    chart.set_x_axis({'name': x_axis_name})
    chart.set_size({'width': 896, 'height': 275})
    chart.set_legend({'none': True})
    report_sheet.insert_chart(cell, chart)


def insert_best_post_info(report_sheet, best_post_info, value_format, post_text, mute):
    report_sheet.merge_range('F76:I76', 'Лучшие посты за неделю', value_format)

    most_liked = best_post_info.get('most_liked', {})
    most_liked_text = _truncate_text(most_liked.get('text'))
    most_liked_metrics = most_liked.get('metrics', {})

    most_viewed = best_post_info.get('most_viewed', {})
    most_viewed_text = _truncate_text(most_viewed.get('text'))
    most_viewed_metrics = most_viewed.get('metrics', {})

    most_reposted = best_post_info.get('most_reposted', {})
    most_reposted_text = _truncate_text(most_reposted.get('text'))
    most_reposted_metrics = most_reposted.get('metrics', {})

    most_commented = best_post_info.get('most_commented', {})
    most_commented_text = _truncate_text(most_commented.get('text'))
    most_commented_metrics = most_commented.get('metrics', {})

    report_sheet.merge_range('B78:F78', 'Больше всего просмотров', value_format)
    report_sheet.merge_range('B79:F84', most_viewed_text, post_text)
    report_sheet.merge_range('B85:C85', 'Реакции', mute)
    report_sheet.merge_range('B86:C86', most_viewed_metrics.get('likes', 0), mute)
    report_sheet.merge_range('E85:F85', 'Репосты', mute)
    report_sheet.merge_range('E86:F86', most_viewed_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('B87:C87', 'Комментарии', mute)
    report_sheet.merge_range('B88:C88', most_viewed_metrics.get('comments', 0), mute)
    report_sheet.merge_range('E87:F87', 'Просмотры', mute)
    report_sheet.merge_range('E88:F88', most_viewed_metrics.get('views', 0), mute)

    report_sheet.merge_range('I78:M78', 'Больше всего лайков', value_format)
    report_sheet.merge_range('I79:M84', most_liked_text, post_text)
    report_sheet.merge_range('I85:J85', 'Реакции', mute)
    report_sheet.merge_range('I86:J86', most_liked_metrics.get('likes', 0), mute)
    report_sheet.merge_range('L85:M85', 'Репосты', mute)
    report_sheet.merge_range('L86:M86', most_liked_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('I87:J87', 'Комментарии', mute)
    report_sheet.merge_range('I88:J88', most_liked_metrics.get('comments', 0), mute)
    report_sheet.merge_range('L87:M87', 'Просмотры', mute)
    report_sheet.merge_range('L88:M88', most_liked_metrics.get('views', 0), mute)

    report_sheet.merge_range('B90:F90', 'Больше всего комментариев', value_format)
    report_sheet.merge_range('B91:F96', most_commented_text, post_text)
    report_sheet.merge_range('B97:C97', 'Реакции', mute)
    report_sheet.merge_range('B98:C98', most_commented_metrics.get('likes', 0), mute)
    report_sheet.merge_range('E97:F97', 'Репосты', mute)
    report_sheet.merge_range('E98:F98', most_commented_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('B99:C99', 'Комментарии', mute)
    report_sheet.merge_range('B100:C100', most_commented_metrics.get('comments', 0), mute)
    report_sheet.merge_range('E99:F99', 'Просмотры', mute)
    report_sheet.merge_range('E100:F100', most_commented_metrics.get('views', 0), mute)

    report_sheet.merge_range('I90:M90', 'Больше всего репостов', value_format)
    report_sheet.merge_range('I91:M96', most_reposted_text, post_text)
    report_sheet.merge_range('I97:J97', 'Реакции', mute)
    report_sheet.merge_range('I98:J98', most_reposted_metrics.get('likes', 0), mute)
    report_sheet.merge_range('L97:M97', 'Репосты', mute)
    report_sheet.merge_range('L98:M98', most_reposted_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('I99:J99', 'Комментарии', mute)
    report_sheet.merge_range('I100:J100', most_reposted_metrics.get('comments', 0), mute)
    report_sheet.merge_range('L99:M99', 'Просмотры', mute)
    report_sheet.merge_range('L100:M100', most_reposted_metrics.get('views', 0), mute)


def insert_graphic_section(workbook, report_sheet, data_sheet, stats_info, value_format, participants_count=0):
    report_sheet.merge_range('G51:H51', 'Графики', value_format)

    daily_date = []
    daily_values = []

    participants_date = []
    participants_values = []

    for stat in stats_info:
        _time = _parse_timestamp(stat)
        daily_date.append(_time.strftime("%d.%m"))
        stats = stat.get('stats', {})
        daily_values.append(stats.get('participants_delta', 0))

    for i in range(len(stats_info) - 1, -1, -1):
        _time = _parse_timestamp(stats_info[i])
        participants_date.append(_time.strftime("%d.%m"))

        stats = stats_info[i].get('stats', {})
        participants_values.append(participants_count)
        participants_count -= stats.get('participants_delta', 0)

    _time = _parse_timestamp(stats_info[0]) - timedelta(days=1)

    participants_date.append(_time.strftime("%d.%m"))
    participants_date.reverse()

    participants_values.append(participants_count)
    participants_values.reverse()

    data_sheet.write_column('A1', daily_date)
    data_sheet.write_column('B1', daily_values)
    data_sheet.write_column('C1', participants_date)
    data_sheet.write_column('D1', participants_values)


    daily_len = len(daily_date)
    daily_chart = workbook.add_chart({"type": "line"})
    daily_chart.set_title({'name': 'Рост подписчиков'})
    daily_chart.add_series({
        'name': 'Подписчики',
        'categories': f'=Данные!$A$1:$A${daily_len}',
        'values': f'=Данные!$B$1:$B${daily_len}',
    })

    participants_data_len = len(participants_values)
    participants_chart = workbook.add_chart({"type": "line"})
    participants_chart.set_title({'name': 'Прирост подписчиков по дням'})
    participants_chart.add_series({
        'name': 'Подписчики',
        'categories': f'=Данные!$C$1:$C${participants_data_len}',
        'values': f'=Данные!$D$1:$D${participants_data_len}',
    })


    daily_chart.set_size({'width': 768, 'height': 250})
    participants_chart.set_size({'width': 768, 'height': 250})
    report_sheet.insert_chart('B53', participants_chart)
    report_sheet.insert_chart('B64', daily_chart)


def generate_group_report_excel(report_data):
    main_info = report_data.get('main_info', {})
    abs_stats_info = report_data.get('abs_stats', {})
    best_post_info = report_data.get('post_info', {})
    stats_info = report_data.get('stats_info')

    aggregated_post_data = report_data.get('aggregated_post_data')

    platform = main_info.get('platform', 'Не указана')
    group_name = main_info.get('group_name', 'Не указано')
    group_name = sanitize(group_name)

    filename = f"{platform}_{group_name}_{datetime.now().strftime('%d.%m.%Y_%H%M%S')}.xlsx"
    xlsx_path = os.path.join(MEDIA_ROOT, 'reports', 'xlsx', group_name)
    os.makedirs(xlsx_path, exist_ok=True)
    filepath = os.path.join(xlsx_path, filename)
    relative_path = os.path.join(MEDIA_URL, 'reports', 'xlsx', group_name, filename).replace('\\', '/')

    workbook = Workbook(filepath)
    report_sheet = workbook.add_worksheet('Отчет')
    report_sheet.set_landscape()
    report_sheet.set_paper(9)
    report_sheet.fit_to_pages(1, 0)
    report_sheet.center_horizontally()
    report_sheet.set_default_row(18.75)
    # report_sheet.set_margins(left=0.7, right=0.7, top=0.75, bottom=0.75)

    data_sheet = workbook.add_worksheet('Данные')
    data_sheet.hide()
    value_format, post_text, mute = get_styles(workbook)

    insert_group_report_header(report_sheet, main_info, value_format)
    insert_group_stats(report_sheet, abs_stats_info, value_format)

    report_sheet.merge_range('E12:J12', 'Агрегированные данные о количестве постов', value_format)

    aggregated_configs = [
        (aggregated_post_data.get('aggregated_likes_counts'),
         'Количество постов агрегированное по количеству лайков',
         'A14', 'Диапазон лайков', ('E', 'F')),
        (aggregated_post_data.get('aggregated_reposts_counts'),
         'Количество постов агрегированное по количеству репостов',
         'A27', 'Диапазон репостов', ('I', 'J')),
        (aggregated_post_data.get('aggregated_comments_counts'),
         'Количество постов агрегированное по количеству комментариев',
         'A39', 'Диапазон комментариев', ('G', 'H')),
    ]
    for agg_data, name, cell, x_axis, data_rows in aggregated_configs:
        insert_aggregated_data_graphic_section(workbook, report_sheet, data_sheet,
                                               agg_data, name, cell, x_axis, data_rows)
    insert_best_post_info(report_sheet, best_post_info, value_format, post_text, mute)
    insert_graphic_section(workbook, report_sheet, data_sheet, stats_info, value_format, abs_stats_info.get('participants_count', 0))

    workbook.close()

    return filepath, relative_path


def generate_group_report_pdf(file_path, folder):
    return convert_xlsx_to_pdf(file_path, folder)
