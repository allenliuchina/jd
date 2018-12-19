import time, os
from .models import GoodType, Promotion, Good
from jd.settings import BASE_DIR
from jd.celery import app


@app.task
def generate_index_html():
    types = GoodType.objects.all()
    for good_type in types:
        good_type.top = Good.objects.filter(type=good_type).order_by('-sales')[:4]
    promotion = Promotion.objects.all()
    cart_count = 0
    context = {
        'types': types,
        'promotion': promotion,
        'cart_count': cart_count,
    }
    from django.template import loader
    temp = loader.get_template('index.html')
    static_html = temp.render(context)
    save_path = os.path.join(BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_html)
