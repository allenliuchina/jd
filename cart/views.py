from django.shortcuts import render
from good.models import Good
from django_redis import get_redis_connection
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required


# Create your views here.
@login_required
def show(request):
    user = request.user
    conn = get_redis_connection('default')
    cart_key = 'cart_%d' % user.id
    cart_dict = conn.hgetall(cart_key)

    total_count = 0
    total_amount = 0
    # 遍历获取购物车中商品的详细信息
    skus = []
    for sku_id, count in cart_dict.items():
        # 根据sku_id获取商品的信息

        sku = Good.objects.get(id=int(sku_id))

        # 计算商品的小计
        amount = sku.price * int(count)

        # 给sku对象增加属性amout和count, 分别保存用户购物车中商品的小计和数量
        sku.count = int(count)
        sku.amount = amount
        # 追加商品的信息
        skus.append(sku)

        # 累加计算用户购物车中商品的总数目和总价格
        total_count += int(count)
        total_amount += amount

    # 组织模板上下文
    context = {
        'total_count': total_count,
        'total_amount': total_amount,
        'skus': skus
    }
    return render(request, 'cart.html', context)


@login_required
def add(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})

    # 获取参数
    sku_id = request.POST.get('sku_id')
    count = request.POST.get('count')  # 数字

    # 参数校验
    if not all([sku_id, count]):
        return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

    # 校验商品id requests urllib
    try:
        sku = Good.objects.get(id=sku_id)
    except Good.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

    # 校验商品数量count
    try:
        count = int(count)
    except Exception as e:
        return JsonResponse({'res': 3, 'errmsg': '商品数量必须为有效数字'})

    # 业务处理: 购物车记录添加
    # 获取redis链接
    conn = get_redis_connection('default')
    # 拼接key
    cart_key = 'cart_%d' % user.id
    # cart_1 : {'1':'3', '2':'5'}
    # hget(key, field)
    cart_count = conn.hget(cart_key, sku_id)

    if cart_count:
        # 如果用户的购物车中已经添加过sku_id商品, 购物车中对应商品的数目需要进行累加
        count += int(cart_count)

    # 校验商品的库存
    if count > sku.stock:
        return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

    # 设置用户购物车中sku_id商品的数量
    # hset(key, field, value)   存在就是修改，不存在就是新增
    conn.hset(cart_key, sku_id, count)

    # 获取用户购物车中商品的条目数
    goods = conn.hgetall(cart_key)
    cart_count = 0
    for v in goods.values():
        cart_count += int(v)

    # 返回应答
    return JsonResponse({'res': 5, 'cart_count': cart_count, 'errmsg': '添加购物车记录成功'})


@login_required
def update(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})

    # 接收参数
    sku_id = request.POST.get('sku_id')
    count = request.POST.get('count')

    # 参数校验
    if not all([sku_id, count]):
        return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

    # 校验商品id requests urllib
    try:
        sku = Good.objects.get(id=sku_id)
    except Good.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

    # 校验商品数量count
    try:
        count = int(count)
    except Exception as e:
        return JsonResponse({'res': 3, 'errmsg': '商品数量必须为有效数字'})

    # 业务处理: 购物车记录更新
    # 获取链接
    conn = get_redis_connection('default')

    # 拼接key
    cart_key = 'cart_%d' % user.id

    # 校验商品的库存量
    if count > sku.stock:
        return JsonResponse({'res': 4, 'errmsg': '商品库存不足'})

    # 更新用户购物车中商品数量
    # hset(key, field, value)
    conn.hset(cart_key, sku_id, count)

    # 返回应答
    return JsonResponse({'res': 5, 'errmsg': '更新购物车记录成功'})


@login_required
def delete(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '请先登录'})

    # 接收参数
    sku_id = request.POST.get('sku_id')
    # 参数校验
    if not all([sku_id]):
        return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

    # 校验商品id requests urllib
    try:
        sku = Good.objects.get(id=sku_id)
    except Good.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '商品信息错误'})

    # 业务处理: 删除用户的购物车记录
    # 获取链接
    conn = get_redis_connection('default')

    # 拼接key
    cart_key = 'cart_%d' % user.id

    # 删除记录
    # hdel(key, *fields)
    conn.hdel(cart_key, sku_id)

    # 返回应答
    return JsonResponse({'res': 3, 'errmsg': '删除购物车记录成功'})
