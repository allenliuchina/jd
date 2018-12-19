from django.shortcuts import render, reverse, redirect
from user.models import Address
from good.models import Good
from django_redis import get_redis_connection
from django.http import JsonResponse
from .models import OrderGoods, OrderInfo
from django.contrib.auth.decorators import login_required
from django.db import transaction
import time
from django.db.models import F


# Create your views here.
@login_required
@transaction.atomic
def before_commit(request):
    user = request.user

    # 获取提交时被选中的商品id
    sku_ids = request.POST.getlist('sku_ids')
    # 若没有商品，则直接跳回首页
    if len(sku_ids) == 0:
        return redirect(reverse('good:index'))

    # 获取收货地址

    addrs = Address.objects.filter(user=user)

    # 拼接key
    cart_key = 'cart_%d' % user.id

    # 连接redis
    conn = get_redis_connection('default')
    # 遍历sku_ids获取用户所要购买的商品的信息
    skus = []
    total_count = 0
    total_amount = 0
    for sku_id in sku_ids:
        # 根据id查找商品的信息
        sku_id = sku_id.replace('\n', '')  # ab 测试使用，vim无法去除末尾的回车符
        sku = Good.objects.get(id=sku_id)

        # 从redis中获取用户所要购买的商品的数量
        count = conn.hget(cart_key, sku_id)

        # 计算的商品小计
        amount = sku.price * int(count)

        # 给sku对象增加属性count和amount
        # 分别保存用户要购买的商品的数目和小计
        sku.count = int(count)
        sku.amount = amount

        # 追加商品的信息
        skus.append(sku)

        # 累加计算用户要购买的商品的总件数和总金额
        total_count += int(count)
        total_amount += amount

    # 运费: 运费表: 100-200  假设为10
    transit_price = 10

    # 实付款
    total_pay = total_amount + transit_price

    # 组织模板上下文
    context = {
        'addrs': addrs,
        'skus': skus,
        'total_count': total_count,
        'total_amount': total_amount,
        'transit_price': transit_price,
        'total_pay': total_pay,
        'sku_ids': ','.join(sku_ids)
    }

    # 使用模板
    return render(request, 'place_order.html', context)


# @login_required
# def commit_order(request):
#     user = request.user
#     if not user.is_authenticated:
#         return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
#
#     # 接收参数
#     addr_id = request.POST.get('addr_id')
#     pay_method = request.POST.get('pay_method')
#     sku_ids = request.POST.get('sku_ids')  # 以,分隔的字符串 3,4
#
#     # 参数校验
#     if not all([addr_id, pay_method, sku_ids]):
#         return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
#
#     # 校验地址id
#     try:
#         addr = Address.objects.get(id=addr_id)
#     except Address.DoesNotExist:
#         return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})
#
#     # 校验支付方式
#     if pay_method not in OrderInfo.PAY_METHODS.keys():
#         return JsonResponse({'res': 3, 'errmsg': '非法的支付方式'})
#
#     # 组织订单信息
#     # 组织订单id: 20180316115930+用户id
#     from datetime import datetime
#     order_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(user.id)
#
#     # 运费
#     transit_price = 10
#
#     # 总数目和总价格
#     total_count = 0
#     total_price = 0
#
#     # todo: 向df_order_info中添加一条记录
#     order = OrderInfo.objects.create(
#         order_id=order_id,
#         user=user,
#         addr=addr,
#         pay_method=pay_method,
#         total_count=total_count,
#         total_price=total_price,
#         transit_price=transit_price
#     )
#
#     # todo: 订单中包含几个商品需要向df_order_goods中添加几条记录
#     # 获取redis链接
#     conn = get_redis_connection('default')
#     # 拼接key
#     cart_key = 'cart_%d' % user.id
#
#     # 将sku_ids分割成一个列表
#     sku_ids = sku_ids.split(',')  # [3,4]
#
#     # 遍历sku_ids，向df_order_goods中添加记录
#     for sku_id in sku_ids:
#         # 根据id获取商品的信息
#         try:
#             sku = Good.objects.get(id=sku_id)
#         except Good.DoesNotExist:
#             return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})
#
#         # 从redis中获取用户要购买的商品的数量
#         count = request.POST.get('count')
#         if not count:
#             count = conn.hget(cart_key, sku_id)
#
#         # 向df_order_goods中添加一条记录
#         OrderGoods.objects.create(
#             order=order,
#             sku=sku,
#             count=count,
#             price=sku.price
#         )
#
#         # 减少商品库存，增加销量
#         sku.stock -= int(count)
#         sku.sales += int(count)
#         sku.save()
#
#         # 累加计算订单中商品的总数目和总价格
#         total_count += int(count)
#         total_price += sku.price * int(count)
#
#     # todo: 更新订单信息中商品的总数目和总价格
#     order.total_count = total_count
#     order.total_price = total_price
#     order.save()
#     conn.hdel(cart_key, *sku_ids)
#     if int(pay_method) == 1:
#         order.order_status = 2
#         order.save()
#
#     # 返回应答
#     return JsonResponse({'res': 5, 'errmsg': '订单创建成功'})


# 悲观锁
# @login_required
# @transaction.atomic
# def commit_order(request):
#     user = request.user
#     if not user.is_authenticated:
#         return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
#     addr_id = request.POST.get('addr_id')
#     pay_method = request.POST.get('pay_method')
#     sku_ids = request.POST.get('sku_ids')
#     if not all([addr_id, pay_method, sku_ids]):
#         return JsonResponse({'res': 1, 'errmsg': '参数不完整'})
#
#     try:
#         addr = Address.objects.get(id=addr_id)
#     except Address.DoesNotExist:
#         return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})
#
#     if pay_method not in OrderInfo.PAY_METHODS.keys():
#         return JsonResponse({'res': 3, 'errmsg': '非法的支付方式'})
#     from datetime import datetime
#     order_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(user.id)
#
#     transit_price = 10
#
#     # 总数目和总价格
#     total_count = 0
#     total_price = 0
#     # 事务记录点
#     sid = transaction.savepoint()
#     try:
#         order = OrderInfo.objects.create(
#             order_id=order_id,
#             user=user,
#             addr=addr,
#             pay_method=pay_method,
#             total_count=total_count,
#             total_price=total_price,
#             transit_price=transit_price
#         )
#
#         conn = get_redis_connection('default')
#         cart_key = 'cart_%d' % user.id
#         sku_ids = sku_ids.split(',')
#         for sku_id in sku_ids:
#             # 根据id获取商品的信息
#             try:
#                 print(1)
#                 sku = Good.objects.select_for_update().get(id=sku_id)  # 获取后加锁,在save之前，其他现线程被阻塞
#                 print(2)
#             except Good.DoesNotExist:
#                 # 回滚
#                 transaction.savepoint_rollback(sid)
#                 return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})
#
#             import time
#             time.sleep(10)
#
#             # 从redis中获取用户要购买的商品的数量
#             count = request.POST.get('count')
#             if not count:
#                 count = conn.hget(cart_key, sku_id)
#                 if not count:
#                     transaction.savepoint_rollback(sid)
#                     return JsonResponse({'res': 6, 'errmsg': '下单失败'})
#                 else:
#                     count = int(count)
#             if count > sku.stock:  # 检验库存
#                 transaction.savepoint_rollback(sid)
#                 return JsonResponse({'res': 7, 'errmsg': '商品库存不足'})
#             # 向df_order_goods中添加一条记录
#             OrderGoods.objects.create(
#                 order=order,
#                 sku=sku,
#                 count=count,
#                 price=sku.price
#             )
#
#             # 减少商品库存，增加销量
#             sku.stock -= int(count)
#             sku.sales += int(count)
#             sku.save()
#             # 累加计算订单中商品的总数目和总价格
#             total_count += int(count)
#             total_price += sku.price * int(count)
#
#         order.total_count = total_count
#         order.total_price = total_price
#         if int(pay_method) == 1:
#             order.order_status = 2
#         order.save()
#     except Exception as e:
#         transaction.savepoint_rollback(sid)
#         return JsonResponse({'res': 6, 'errmsg': '下单失败'})
#     conn.hdel(cart_key, *sku_ids)
#     return JsonResponse({'res': 5, 'errmsg': '订单创建成功'})
#

# 乐观锁
@login_required
@transaction.atomic
def commit_order(request):
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})
    addr_id = request.POST.get('addr_id')
    pay_method = request.POST.get('pay_method')
    sku_ids = request.POST.get('sku_ids')
    count = request.POST.get('count')
    if not all([addr_id, pay_method, sku_ids]):
        return JsonResponse({'res': 1, 'errmsg': '参数不完整'})

    try:
        addr = Address.objects.get(id=addr_id)
    except Address.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '地址信息错误'})
    if addr.user.id != user.id:
        return JsonResponse({'res': 2, 'errmsg': '地址错误'})
    if pay_method not in OrderInfo.PAY_METHODS.keys():
        return JsonResponse({'res': 3, 'errmsg': '非法的支付方式'})
    from datetime import datetime
    order_id = datetime.now().strftime("%Y%m%d%H%M%S") + str(user.id)

    transit_price = 10
    total_count = 0
    total_price = 0
    # 事务记录点
    sid = transaction.savepoint()
    try:
        order_info = OrderInfo.objects.create(
            order_id=order_id,
            user=user,
            pay_method=pay_method,
            addr=addr,
            total_count=total_count,
            total_price=total_price,
            transit_price=transit_price,
        )
        conn = get_redis_connection('default')
        cart_key = 'cart_%d' % user.id
        sku_ids = sku_ids.split(',')
        for sku_id in sku_ids:
            for i in range(3):
                start = time.time()
                try:
                    good = Good.objects.get(id=sku_id)
                    # if user.username == 'user':
                    #     time.sleep(10)

                except Good.DoesNotExist:
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({'res': 4, 'errmsg': '商品信息错误'})
                if not count:
                    count = conn.hget(cart_key, sku_id)
                    if not count:
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({'res': 6, 'errmsg': '下单失败'})

                count = int(count)
                if good.stock < count:
                    transaction.savepoint_rollback(sid)
                    return JsonResponse({'res': 7, 'errmsg': '商品库存不足'})
                rep = Good.objects.filter(id=sku_id, stock=good.stock).update(stock=good.stock - count,
                                                                              sales=good.sales + count)  # 确保没有别的线程修改过,rep返回修改的行数
                if rep == 0:
                    if i == 2:
                        transaction.savepoint_rollback(sid)
                        return JsonResponse({'res': 6, 'errmsg': '下单失败'})
                    else:
                        continue
                OrderGoods.objects.create(
                    order=order_info,
                    sku=good,
                    count=count,
                    price=good.price
                )
                total_count += count
                total_price += total_count * good.price
                break
        order_info.total_count = total_count
        order_info.total_price = total_price + transit_price
        order_info.save(update_fields=['total_count', 'total_price'])
    except Exception as e:
        transaction.savepoint_rollback(sid)
        return JsonResponse({'res': 6, 'errmsg': '下单失败'})
    conn.hdel(cart_key, *sku_ids)
    return JsonResponse({'res': 5, 'errmsg': '下单成功'})


@login_required
def pay_order(request):
    # 登录验证
    user = request.user
    if not user.is_authenticated:
        return JsonResponse({'res': 0, 'errmsg': '用户未登录'})

    # 接收参数
    order_id = request.POST.get('order_id')

    # 参数校验
    if not all([order_id]):
        return JsonResponse({'res': 1, 'errmsg': '缺少参数'})

    # 校验订单id
    try:
        order = OrderInfo.objects.get(order_id=order_id,
                                      user=user,
                                      order_status=1,  # 待支付
                                      pay_method=1,  # 支付宝支付
                                      )
    except OrderInfo.DoesNotExist:
        return JsonResponse({'res': 2, 'errmsg': '无效订单id'})

    return JsonResponse({'res': 3, 'pay_url': 'baidu.com', 'errmsg': 'OK'})


def pay_check(request):
    pass


def cancel(request, id):
    user = request.user
    start = time.time()
    order = OrderInfo.objects.get(order_id=id)
    if order.user.id != user.id:
        return redirect(reverse('good:index'))
    goods = order.ordergoods_set.all()
    for good in goods:
        good.sku.stock = F('stock') + good.count
        good.sku.sales = F('sales') - good.count
        good.sku.save(update_fields=['stock', 'sales'])
        # Good.objects.filter(pk=good.sku.id).update(stock=good.sku.stock + good.count, sales=good.sku.sales - good.count)
    print('save', time.time() - start)
    order.delete()
    print('delete;', time.time() - start)
    return redirect(reverse('user:order', args=[1]))


@login_required
def fast_buy(request, id, count):
    good = Good.objects.filter(pk=id).first()
    good.count = count
    good.unite = 1
    good.amount = count * good.price
    if count > good.stock:
        return JsonResponse({'res': 5})
    return JsonResponse({'res': 0})


@login_required
def fast_commit(request, id, count):
    user = request.user
    addr = Address.objects.filter(user=user)
    good = Good.objects.filter(pk=id).first()
    transit_price = 10
    total_amount = good.price * count
    # 实付款
    total_pay = total_amount + transit_price
    good.count = count
    good.amount = good.price * count
    good.unite = '部'
    # 组织模板上下文
    context = {
        'addrs': addr,
        'skus': [good],
        'total_count': count,
        'total_amount': total_amount,
        'transit_price': transit_price,
        'total_pay': total_pay,
        'sku_ids': good.id,
        'fast': 'true',
    }

    # 使用模板
    return render(request, 'place_order.html', context)
