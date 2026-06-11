html_confirmation_message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #333;">Подтверждение email</h2>
    <p>Здравствуйте!</p>
    <p>Для подтверждения email адреса нажмите на кнопку ниже:</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href=\"%s\" target=_blank style="background-color: #4CAF50; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Подтвердить</a>
    </div>
    <p style="color: #666; font-size: 12px;">Или перейдите по <a href=\"%s\" target=_blank>ссылке</a></p>
    <hr style="margin: 20px 0;">
    <p style="color: #999; font-size: 12px;">Если вы не запрашивали подтверждение, проигнорируйте это письмо.</p>
</body>
</html>"""

html_password_reset_message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #333;">Сброс пароля</h2>
    <p>Здравствуйте!</p>
    <p>Вы запросили сброс пароля. Для установки нового пароля нажмите на кнопку ниже:</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href=\"%s\" target=_blank style="background-color: #f44336; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Сбросить пароль</a>
    </div>
    <p style="color: #666; font-size: 12px;">Или перейдите по <a href=\"%s\" target=_blank>ссылке</a></p>
    <hr style="margin: 20px 0;">
    <p style="color: #999; font-size: 12px;">Если вы не запрашивали сброс пароля, просто проигнорируйте это письмо. Ваш пароль останется без изменений.</p>
    <p style="color: #999; font-size: 12px;">Ссылка действительна в течение 15 минут.</p>
</body>
</html>"""

html_admin_notify_message = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
</head>
<body style="font-family: Arial, sans-serif; max-width: 500px; margin: 0 auto; padding: 20px;">
    <h2 style="color: #333;">Подтверждение получения уведомлений</h2>
    <p>Для активации уведомлений на этот email адрес нажмите на кнопку ниже:</p>
    <div style="text-align: center; margin: 30px 0;">
        <a href=\"%s\" target="_blank" style="background-color: #2196F3; color: white; padding: 12px 24px; text-decoration: none; border-radius: 4px; display: inline-block;">Подтвердить отправку уведомлений</a>
    </div>
    <p style="color: #666; font-size: 12px;">Или перейдите по <a href=\"%s\" target="_blank">ссылке</a></p>
    <hr style="margin: 20px 0;">
    <p style="color: #999; font-size: 12px;">Если вы не запрашивали подключение уведомлений, проигнорируйте это письмо.</p>
    <p style="color: #999; font-size: 12px;">После подтверждения вы будете получать уведомления о важных событиях на этот email.</p>
</body>
</html>"""


def prepare_message(token, _type) -> str:
    match _type:
        case 'reset':
            url = f'https://socialpulse.sandbox.com/reset?token={token}'
            message = html_password_reset_message % (url, url)
        case 'activate':
            url = f'https://socialpulse.sandbox.com/email/activate?token={token}'
            message = html_confirmation_message % (url, url)
        case 'admin':
            url = f'https://socialpulse.sandbox.com/email/activate?token={token}'
            message = html_admin_notify_message % (url, url)
        case _:
            message = None

    return message
