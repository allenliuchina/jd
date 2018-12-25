import os
from .models import GoodType, Promotion, Good
from django.conf import settings
from jd.celery import app
from django.core.cache import cache
from django_redis import get_redis_connection
from django.core.paginator import Paginator


@app.task
def generate_index_html():
    types = GoodType.objects.all()
    for good_type in types:
        good_type.top = Good.objects.filter(type=good_type).order_by('-sales')[:4]
    context = {
        'types': types,
    }
    cache.set('index_context', context, 3600)
    promotion = Promotion.objects.all()
    cart_count = 0
    context['promotion'] = promotion
    context['cart_count'] = cart_count
    from django.template import loader
    temp = loader.get_template('index.html')
    static_html = temp.render(context)
    save_path = os.path.join(settings.BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_html)


# @app.task
# def create_index_cache():
#     types = GoodType.objects.all()
#     for good_type in types:
#         good_type.top = Good.objects.filter(type=good_type).order_by('-sales')[:4]
#     context = {
#         'types': types,
#     }
#     cache.set('index_context', context, 3000)


@app.task
def create_new_good_cache():
    conn = get_redis_connection()
    types = GoodType.objects.all()
    for good_type in types:
        new_goods_type = 'new_goods_%s' % good_type.id
        new_goods = Good.objects.filter(type=good_type).order_by('-create_time')[:2]
        # conn.ltrim(new_goods_type, 0, 0)
        conn.delete(new_goods_type)
        for good in new_goods:
            conn.rpush(new_goods_type, good.id)


@app.task
def create_page_cache():
    conn = get_redis_connection()
    types = GoodType.objects.all()
    for good_type in types:
        goods = Good.objects.filter(type=good_type).order_by('-sales').all()
        paginator = Paginator(goods, 20)
        for num in range(1, 4):
            list_id_num = 'list_%s_%s' % (good_type.id, num)
            h_list_id_num = 'h_list_%s_%s' % (good_type.id, num)
            skus = paginator.page(num)
            # conn.ltrim(list_id_num, 0, 0)
            conn.delete(list_id_num)
            for sku in skus:
                conn.rpush(list_id_num, sku.id)
            if skus.has_next():
                number = skus.next_page_number()
                conn.hset(h_list_id_num, 'next', str(number))
            if skus.has_previous():
                number = skus.previous_page_number()
                conn.hset(h_list_id_num, 'pre', str(number))
