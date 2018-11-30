from django.shortcuts import render, redirect, reverse
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login as log_in, logout
from django_redis import get_redis_connection
from good.models import Good
from .models import Address
from order.models import OrderInfo, OrderGoods
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from itsdangerous import TimedJSONWebSignatureSerializer
from django.http import HttpResponse
from django.contrib import messages


# Create your views here.
def login(request):
    if request.method == 'GET':
        username = request.COOKIES.get('username')
        # errmsg = request.COOKIES.get('errmsg')
        context = {}
        # if errmsg:
        #     context['errmsg'] = errmsg.encode('latin-1').decode()
        if username:
            context['username'] = username
        response = render(request, 'login.html', context)
        response.delete_cookie('errmsg')
        return response
    username = request.POST.get('username')
    password = request.POST.get('pwd')
    remember = request.POST.getlist('remember')
    user = authenticate(username=username, password=password)
    if user:
        log_in(request, user)
        response = redirect(reverse('good:index'))
        if request.GET.get('next'):
            response = redirect(request.GET['next'])
        if remember:
            response.set_cookie('username', username, max_age=60 * 60 * 24 * 7)
        else:
            response.delete_cookie('username')
        return response
    response = redirect(reverse('user:login'))
    # response.set_cookie('errmsg', '用户名或者密码错误'.encode().decode('latin-1'))  # cookie中设置不了中文
    messages.add_message(request, messages.ERROR, '用户名或者密码错误')
    return response


def register(request):
    if request.method == 'GET':
        return render(request, 'register.html')
    username = request.POST.get('username')
    password = request.POST.get('pwd')
    email = request.POST.get('email')
    user = User.objects.create_user(username, email, password)
    if user:
        user.is_active = False
        user.save()
        # 激活邮件
        jws = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 60)
        token = jws.dumps(user.id)  # token 可以被解密，不要存储敏感信息

        token = token.decode()
        subject = '天天生鲜欢迎信息'
        message = ''
        sender = settings.EMAIL_FROM
        receiver = ['772075034@qq.com']
        html_message = """
                    <h1>%s, 欢迎您成为天天生鲜注册会员</h1>
                    请点击一下链接激活您的账号(1小时之内有效)<br/>
                    <a href="http://127.0.0.1:8000/user/active/%s">http://127.0.0.1:8000/user/active/%s</a>
                """ % (username, token, token)
        send_mail(subject, message, sender, receiver, html_message=html_message)
        return redirect(reverse('goods:index'))


def activate(request, token):
    jws = TimedJSONWebSignatureSerializer(settings.SECRET_KEY, expires_in=60 * 60)
    id = jws.loads(token)
    if not id:
        return HttpResponse('无效的token')
    user = User.objects.get(id=id)
    user.is_active = True
    user.save()
    return redirect(reverse('good:index'))


@login_required
def user(request):
    user = request.user
    history_key = 'seen_%d' % user.id

    # lrange(key, start, stop) 返回是列表
    # 获取用户最新浏览的5个商品的id
    conn = get_redis_connection('default')
    sku_ids = conn.lrange(history_key, 0, 4)  # [1, 3, 5, 2]

    skus = []
    for sku_id in sku_ids:
        # 根据商品的id查询商品的信息
        sku = Good.objects.get(id=sku_id)
        # 追加到skus列表中
        skus.append(sku)

    context = {'skus': skus, 'page': 'user'}
    return render(request, 'user_center_info.html', context)


@login_required
def order(request, page):
    user = request.user
    # 查询所有订单
    info_msg = 1  # 若有订单则为1
    try:
        order_infos = OrderInfo.objects.filter(user=user).all()
    except OrderInfo.DoesNotExist:
        info_msg = 0

    if len(order_infos) == 0:
        info_msg = 0
    context = {
        'page': 'order',
        'info_msg': info_msg,
    }
    if info_msg == 1:

        for order_info in order_infos:
            order_goods = OrderGoods.objects.filter(order=order_info)
            for order_good in order_goods:
                # 商品小计
                amount = order_good.price * order_good.count

                order_good.amount = amount

            order_info.order_goods = order_goods
            order_info.status_title = OrderInfo.ORDER_STATUS[order_info.order_status]
            # order_info.status = order_info.ORDER_STATUS_CHOICES[order_info.order_status-1][1]

        # 分页操作
        from django.core.paginator import Paginator
        paginator = Paginator(order_infos, 3)

        # 处理页码
        page = int(page)

        if page > paginator.num_pages:
            # 默认获取第1页的内容
            page = 1

        # 获取第page页内容, 返回Page类的实例对象
        order_infos_page = paginator.page(page)

        # 页码处理
        # 如果分页之后页码超过5页，最多在页面上只显示5个页码：当前页前2页，当前页，当前页后2页
        # 1) 分页页码小于5页，显示全部页码
        # 2）当前页属于1-3页，显示1-5页
        # 3) 当前页属于后3页，显示后5页
        # 4) 其他请求，显示当前页前2页，当前页，当前页后2页
        num_pages = paginator.num_pages
        if num_pages < 5:
            # 1-num_pages
            pages = range(1, num_pages + 1)
        elif page <= 3:
            pages = range(1, 6)
        elif num_pages - page <= 2:
            # num_pages-4, num_pages
            pages = range(num_pages - 4, num_pages + 1)
        else:
            # page-2, page+2
            pages = range(page - 2, page + 3)

        context = {
            'page': 'order',
            'order_infos': order_infos,
            'info_msg': info_msg,
            'pages': pages,
            'order_infos_page': order_infos_page
        }
    return render(request, 'user_center_order.html', context)


@login_required
def log_out(request):
    logout(request)
    return redirect(reverse('good:index'))


@login_required
def address(request):
    user = request.user
    if request.method == 'GET':
        address = Address.objects.filter(user=user, is_default=True).first()
        having_address = Address.objects.filter(user=user).all()
        return render(request, 'user_center_site.html',
                      {'address': address, 'have_address': having_address, 'page': 'address'})
    receiver = request.POST['receiver']
    addr = request.POST['direction']
    mail_code = request.POST['mail_code']
    phone = request.POST['phone_number']
    is_default = request.POST['is_default']
    if is_default:
        is_default = True
    else:
        is_default = False
    address = Address(receiver=receiver, addr=addr, phone=phone, zip_code=mail_code, is_default=is_default,
                      user=user)
    address.save()
    return redirect(reverse('user:address'))


def test(request):
    pass
