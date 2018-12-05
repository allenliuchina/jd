import time, os
from .models import GoodType, Promotion
from jd.settings import BASE_DIR
from jd.celery import app


@app.task
def add(a, b):
    time.sleep(5)
    return a + b


@app.task
def generate_index_html():
    # time.sleep(10)
    types = GoodType.objects.all()
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
