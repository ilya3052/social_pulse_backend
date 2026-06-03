import os
import subprocess

from social_pulse.settings import MEDIA_ROOT, MEDIA_URL


BASE_CELL_FORMAT = {
    'font_name': 'Times New Roman',
    'font_size': 14,
    'align': 'center',
    'valign': 'vcenter',
    'bg_color': '#F8F9FA',
    'border': 1,
    'border_color': '#BFBFBF',
}


def make_format(workbook, remove=None, **overrides):
    props = {**BASE_CELL_FORMAT}
    if remove:
        for key in remove:
            props.pop(key, None)
    props.update(overrides)
    return workbook.add_format(props)


def convert_xlsx_to_pdf(file_path, folder):
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
