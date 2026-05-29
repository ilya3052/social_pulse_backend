import math
import os
import subprocess
from datetime import datetime

from xlsxwriter import Workbook

from social_pulse.settings import MEDIA_ROOT, MEDIA_URL


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
    post_text.set_font_size(14)
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


def insert_best_post_info(report_sheet, best_post_info, value_format, post_text, mute):
    report_sheet.merge_range('F13:I13', 'Лучшие посты за неделю', value_format)

    most_liked = best_post_info.get('most_liked', {})
    most_liked_text = most_liked.get('text')[:147] + '...' if len(most_liked.get('text')) >= 150 else most_liked.get(
        'text')
    most_liked_metrics = most_liked.get('metrics', {})

    most_viewed = best_post_info.get('most_viewed', {})
    most_viewed_text = most_viewed.get('text')[:147] + '...' if len(
        most_viewed.get('text')) >= 150 else most_viewed.get(
        'text')
    most_viewed_metrics = most_viewed.get('metrics', {})

    most_reposted = best_post_info.get('most_reposted', {})
    most_reposted_text = most_reposted.get('text')[:147] + '...' if len(
        most_reposted.get('text')) >= 150 else most_reposted.get(
        'text')
    most_reposted_metrics = most_reposted.get('metrics', {})

    most_commented = best_post_info.get('most_commented', {})
    most_commented_text = most_commented.get('text')[:147] + '...' if len(
        most_commented.get('text')) >= 150 else most_commented.get(
        'text')
    most_commented_metrics = most_commented.get('metrics', {})

    report_sheet.merge_range('B15:F15', 'Больше всего просмотров', value_format)
    report_sheet.merge_range('B16:F19', most_viewed_text, post_text)
    report_sheet.merge_range('B20:C20', 'Реакции', mute)
    report_sheet.merge_range('B21:C21', most_viewed_metrics.get('likes', 0), mute)
    report_sheet.merge_range('E20:F20', 'Репосты', mute)
    report_sheet.merge_range('E21:F21', most_viewed_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('B22:C22', 'Комментарии', mute)
    report_sheet.merge_range('B23:C23', most_viewed_metrics.get('comments', 0), mute)
    report_sheet.merge_range('E22:F22', 'Просмотры', mute)
    report_sheet.merge_range('E23:F23', most_viewed_metrics.get('views', 0), mute)

    report_sheet.merge_range('I15:M15', 'Больше всего лайков', value_format)
    report_sheet.merge_range('I16:M19', most_liked_text, post_text)
    report_sheet.merge_range('I20:J20', 'Реакции', mute)
    report_sheet.merge_range('I21:J21', most_liked_metrics.get('likes', 0), mute)
    report_sheet.merge_range('L20:M20', 'Репосты', mute)
    report_sheet.merge_range('L21:M21', most_liked_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('I22:J22', 'Комментарии', mute)
    report_sheet.merge_range('I23:J23', most_liked_metrics.get('comments', 0), mute)
    report_sheet.merge_range('L22:M22', 'Просмотры', mute)
    report_sheet.merge_range('L23:M23', most_liked_metrics.get('views', 0), mute)

    report_sheet.merge_range('B27:F27', 'Больше всего комментариев', value_format)
    report_sheet.merge_range('B28:F31', most_commented_text, post_text)
    report_sheet.merge_range('B32:C32', 'Реакции', mute)
    report_sheet.merge_range('B33:C33', most_commented_metrics.get('likes', 0), mute)
    report_sheet.merge_range('E32:F32', 'Репосты', mute)
    report_sheet.merge_range('E33:F33', most_commented_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('B34:C34', 'Комментарии', mute)
    report_sheet.merge_range('B35:C35', most_commented_metrics.get('comments', 0), mute)
    report_sheet.merge_range('E34:F34', 'Просмотры', mute)
    report_sheet.merge_range('E35:F35', most_commented_metrics.get('views', 0), mute)

    report_sheet.merge_range('I27:M27', 'Больше всего репостов', value_format)
    report_sheet.merge_range('I28:M31', most_reposted_text, post_text)
    report_sheet.merge_range('I32:J32', 'Реакции', mute)
    report_sheet.merge_range('I33:J33', most_reposted_metrics.get('likes', 0), mute)
    report_sheet.merge_range('L32:M32', 'Репосты', mute)
    report_sheet.merge_range('L33:M33', most_reposted_metrics.get('reposts', 0), mute)
    report_sheet.merge_range('I34:J34', 'Комментарии', mute)
    report_sheet.merge_range('I35:J35', most_reposted_metrics.get('comments', 0), mute)
    report_sheet.merge_range('L34:M34', 'Просмотры', mute)
    report_sheet.merge_range('L35:M35', most_reposted_metrics.get('views', 0), mute)


def insert_graphic_section(workbook, report_sheet, data_sheet, stats_info, value_format):
    report_sheet.merge_range('G38:H38', 'Графики', value_format)

    daily_date = []
    daily_values = []

    hourly_hour = []
    hourly_likes = []
    hourly_views = []
    for stat in stats_info:
        if stat.get('type') == 'DAILY':
            _time = datetime.fromisoformat(stat.get('timestamp'))
            daily_date.append(_time.strftime("%d.%m"))
            daily_values.append(stat.get('stats', {}).get('participants_delta', 0))
            continue
        _time = datetime.fromisoformat(stat.get('timestamp'))
        hourly_hour.append(_time.strftime("%H:%M"))
        hourly_likes.append(stat.get('stats', {}).get('likes_count', 0))
        hourly_views.append(stat.get('stats', {}).get('views_count', 0))

    daily_len = len(daily_date)
    hourly_len = len(hourly_hour)

    data_sheet.write_column(0, 0, daily_date)
    data_sheet.write_column(0, 1, daily_values)

    data_sheet.write_column(0, 3, hourly_hour)
    data_sheet.write_column(0, 4, hourly_likes)
    data_sheet.write_column(0, 5, hourly_views)

    daily_chart = workbook.add_chart({"type": "line"})
    daily_chart.set_title({'name': 'Рост подписчиков'})
    daily_chart.add_series({
        'name': 'Подписчики',
        'categories': f'=Данные!$A$1:$A${daily_len}',
        'values': f'=Данные!$B$1:$B${daily_len}',
    })
    daily_chart.set_size({'width': 384, 'height': 250})
    report_sheet.insert_chart('A40', daily_chart)

    hourly_chart = workbook.add_chart({"type": "line"})
    hourly_chart.set_title({'name': 'Активность по часам'})
    hourly_chart.add_series({
        'name': 'Лайки',
        'categories': f'=Данные!$D$1:$D${hourly_len}',
        'values': f'=Данные!$E$1:E${hourly_len}',
    })
    hourly_chart.add_series({
        'name': 'Просмотры',
        'categories': f'=Данные!$D$1:$D${hourly_len}',
        'values': f'=Данные!$F$1:F${hourly_len}',
    })
    hourly_chart.set_size({'width': 384, 'height': 250})
    report_sheet.insert_chart('I40', hourly_chart)


def generate_group_report_excel(report_data):
    main_info = report_data.get('main_info', {})
    abs_stats_info = report_data.get('abs_stats', {})
    best_post_info = report_data.get('post_info', {})
    stats_info = report_data.get('stats_info')

    platform = main_info.get('platform', 'Не указана')
    group_name = main_info.get('group_name', 'Не указано').replace(' ', '_')

    filename = f"{platform}_{group_name}_{datetime.now().strftime('%d.%m.%Y_%H%M%S')}.xlsx"
    xlsx_path = os.path.join(MEDIA_ROOT, 'reports', 'xlsx', group_name)
    os.makedirs(xlsx_path, exist_ok=True)
    filepath = os.path.join(xlsx_path, filename)
    relative_path = os.path.join(MEDIA_URL, 'reports', 'xlsx', group_name, filename).replace('\\', '/')

    workbook = Workbook(filepath)
    report_sheet = workbook.add_worksheet('Отчет')
    report_sheet.set_landscape()
    report_sheet.set_paper(9)
    report_sheet.set_default_row(18.75)

    data_sheet = workbook.add_worksheet('Данные')
    data_sheet.hide()
    value_format, post_text, mute = get_styles(workbook)

    insert_group_report_header(report_sheet, main_info, value_format)
    insert_group_stats(report_sheet, abs_stats_info, value_format)
    insert_best_post_info(report_sheet, best_post_info, value_format, post_text, mute)
    insert_graphic_section(workbook, report_sheet, data_sheet, stats_info, value_format)

    workbook.close()

    return filepath, relative_path


def generate_group_report_pdf(file_path, folder):
    out_dir = os.path.join(MEDIA_ROOT, 'reports', 'pdf', folder)
    os.makedirs(out_dir, exist_ok=True)

    command_convert = [
        'soffice',
        '--headless',
        '--convert-to', 'pdf:calc_pdf_Export:Zoom=100',
        '--outdir', out_dir,
        file_path
    ]
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path = os.path.join(out_dir, f"{base_name}.pdf")
    relative_path = os.path.join(MEDIA_URL, os.path.relpath(output_path, MEDIA_ROOT)).replace('\\', '/')

    subprocess.run(command_convert, capture_output=True, text=True, check=True)
    os.remove(file_path)
    return output_path, relative_path
