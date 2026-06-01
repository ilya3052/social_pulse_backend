html_message = f"""<!DOCTYPE html>
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

def prepare_message(token) -> str:
    url = f'https://socialpulse.sandbox.com/email/activate?token={token}'
    message = html_message % (url, url)

    return message
