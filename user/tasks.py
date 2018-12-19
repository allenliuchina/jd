from jd.celery import app
from jd import settings
from django.core.mail import send_mail
from itsdangerous import TimedJSONWebSignatureSerializer


@app.task
def send(to_email, username, user_id):
    serializer = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, 60 * 60)
    info = {'confirm': user_id}
    token = serializer.dumps(info)
    token = token.decode()
    subject = '天天生鲜欢迎信息'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = """
                        <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
                        请点击以下链接激活您的账户(1个小时内有效)<br/>
                        <a href="http://%s/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
                    """ % (settings.SITE_URL, username, token, token)

    # 发送激活邮件
    # send_mail(subject=邮件标题, message=邮件正文,from_email=发件人, recipient_list=收件人列表)
    send_mail(subject, message, sender, receiver, html_message=html_message)
