from django.shortcuts import render, redirect, reverse
from .models import GoodType, Good, Promotion
from django_redis import get_redis_connection
from haystack.views import SearchView
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.core.cache import cache
import time


def good_list(request, id, num):
    # start = time.time()
    try:
        good_type = GoodType.objects.get(pk=id)
    except GoodType.DoesNotExist:
        return redirect(reverse('good:index'))
    conn = get_redis_connection()
    list_id_num = 'list_%s_%s' % (id, num)
    h_list_id_num = 'h_list_%s_%s' % (id, num)
    skus = conn.lrange(list_id_num, 0, 20)
    if not skus:
        goods = Good.objects.filter(type=good_type).order_by('-sales').all()
        paginator = Paginator(goods, 20)
        skus = paginator.page(num)
        for sku in skus:
            conn.rpush(list_id_num, sku.id)
        if skus.has_next():
            number = skus.next_page_number()
            conn.hset(h_list_id_num, 'next', str(number))
        if skus.has_previous():
            number = skus.previous_page_number()
            conn.hset(h_list_id_num, 'pre', str(number))
        skus = conn.lrange(list_id_num, 0, 20)
    goods = []
    pages = {
        'next': False,
        'pre': False,
        'next_number': None,
        'pre_number': None,
    }
    for sku in skus:
        good = Good.objects.get(id=int(sku.decode()))
        goods.append(good)
    next_number = conn.hget(h_list_id_num, 'next')
    if next_number:
        pages['next'] = True
        pages['next_number'] = int(next_number)
    pre_number = conn.hget(h_list_id_num, 'pre')
    if pre_number:
        pages['pre'] = True
        pages['pre_number'] = int(pre_number)

    new_goods_type = 'new_goods_%s' % id
    new_goods_list = conn.lrange(new_goods_type, 0, 5)
    if not new_goods_list:
        new_goods = Good.objects.filter(type=good_type).order_by('-create_time')[:2]
        for new_good in new_goods:
            conn.rpush(new_goods_type, new_good.id)
    else:
        new_goods = []
        for new_good in new_goods_list:
            try:
                good = Good.objects.get(id=int(new_good))
            except Good.DoesNotExist:
                continue
            new_goods.append(good)

    cart_count = 0
    if request.user.is_authenticated:
        cart_key = 'cart_%s' % request.user.id
        cart_goods = conn.hgetall(cart_key)
        for v in cart_goods.values():
            cart_count += int(v)
    # print(time.time() - start)
    # return JsonResponse({'a': 'c'})
    return render(request, 'list.html',
                  {'type': good_type, 'skus_page': goods, 'new_skus': new_goods, 'cart_count': cart_count,
                   'pages': pages, })


def detail(request, id):
    start = time.time()
    try:
        good = Good.objects.get(pk=id)
    except Good.DoesNotExist:
        return redirect(reverse('good:index'))
    cart_count = 0
    conn = get_redis_connection()
    if request.user.is_authenticated:
        seen_good = 'seen_%s' % request.user.id
        cart_key = 'cart_%s' % request.user.id
        has_seen = conn.lrange(seen_good, 0, 5)
        if str(id).encode() not in has_seen:
            conn.lpush(seen_good, id)
        conn.ltrim(seen_good, 0, 4)
        goods = conn.hgetall(cart_key)
        for v in goods.values():
            cart_count += int(v)
    comments = good.goodcomment_set.all()
    new_goods_type = 'new_goods_%s' % good.type.id
    new_goods_list = conn.lrange(new_goods_type, 0, 2)
    if not new_goods_list:
        new_goods = Good.objects.filter(type=good.type).order_by('-create_time')[:2]
        new_goods = list(new_goods)
        for good in new_goods:
            conn.rpush(new_goods_type, good.id)
    else:
        new_goods = []
        for good_id in new_goods_list:
            try:
                new_good = Good.objects.get(id=int(good_id))
            except Good.DoesNotExist:
                continue
            new_goods.append(new_good)
    # print(time.time() - start)
    return render(request, 'detail.html',
                  {'sku': good, 'comments': comments, 'new_goods': new_goods, 'cart_count': cart_count})


def index(request):
    # start = time.time()
    if request.user.is_authenticated:
        conn = get_redis_connection()
        # print(time.time())
        context = cache.get('index_context')
        if context is None:
            types = GoodType.objects.all()
            for good_type in types:
                good_type.top = Good.objects.filter(type=good_type).order_by('-sales')[:4]
            context = {
                'types': types,
            }
            cache.set('index_context', context, 3600)
        promotion = Promotion.objects.all()
        context['promotion'] = promotion
        cart_key = 'cart_%s' % request.user.id
        goods = conn.hgetall(cart_key)
        cart_count = 0
        for v in goods.values():
            cart_count += int(v)
        context['cart_count'] = cart_count
        # print(time.time() - start)
        return render(request, 'index.html', context)
        # return HttpResponse('ok')
    # 没有登录的话，直接返回生成的静态文件
    return redirect('/static/index.html')


# 直接存储id,后期通过id取good，每个耗时大约1毫秒，首页共24个good，不如直接cache （types）耗时7~9毫秒
# def index(request):
#     start = time.time()
#     if request.user.is_authenticated:
#         conn = get_redis_connection()
#         print('first cache connet', time.time())
#
#         types = GoodType.objects.all()
#         print('types:', time.time() - start)
#         a = time.time()
#         for good_type in types:
#             type_top = 'good_type_top_%s' % good_type.id
#             tops = conn.lrange(type_top, 0, 4)
#             if not tops:
#                 top_goods = Good.objects.filter(type=good_type).order_by('-sales')[:4]
#                 top_goods = list(top_goods)
#                 print(type(top_goods))
#                 for top_good in top_goods:
#                     print(type(top_good))
#                     conn.rpush(type_top, top_good.id)
#             else:
#                 top_goods = []
#                 for top_id in tops:
#                     b = time.time()
#                     good = Good.objects.get(id=int(top_id))
#                     print('good_get_single:', time.time() - b)
#                     # print(type(good))
#                     top_goods.append(good)
#             good_type.top = top_goods
#             print('for :', time.time() - a)
#         context = {
#             'types': types,
#         }
#
#         promotion = Promotion.objects.all()
#         context['promotion'] = promotion
#         cart_key = 'cart_%s' % request.user.id
#         goods = conn.hgetall(cart_key)
#         cart_count = 0
#         for v in goods.values():
#             cart_count += int(v)
#         context['cart_count'] = cart_count
#         print(time.time() - start)
#         return render(request, 'index.html', context)
#         # return HttpResponse('ok')
#     # 没有登录的话，直接返回生成的静态文件
#     return redirect('/static/index.html')


class Search(SearchView):
    def extra_context(self):
        cart_count = 0
        if self.request.user.is_authenticated:
            conn = get_redis_connection()
            cart_key = 'cart_%s' % self.request.user.id
            goods = conn.hgetall(cart_key)
            cart_count = 0
            for v in goods.values():
                cart_count += int(v)
        context = {'cart_count': cart_count}
        return context


#
# import forgery_py
# import random
# from django.http import HttpResponse
# import time
#
#
# def mysql_test(request):
#     start = time.time()
#     for i in range(1, 1000000):
#
#         good = Good.objects.create(
#             name=forgery_py.internet.user_name(True),
#             price=random.randint(1000, 10000),
#             desc=forgery_py.lorem_ipsum.sentence(),
#             stock=100,
#             type_id=random.randint(1, 6)
#         )
#         try:
#             good.image = 'image/' + forgery_py.internet.user_name(True)
#             good.save()
#         except Exception as e:
#             print(e)
#             continue
#
#         i += 1
#     print(time.time() - start)
#     return HttpResponse('ok')
# from django.http import HttpResponse
#
#
# def test(request):
#     a = time.time()
#     goods = Good.objects.filter(name='360').all()
#     for g in goods:
#         print(g.id)
#     print(time.time() - a)
#     goods = list(goods)
#     return HttpResponse('ok')
