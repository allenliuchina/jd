from good.models import Good,GoodType,Promotion
import os
from jd.settings import BASE_DIR


def generate_index_html():
    types = GoodType.objects.all()
    promotion = Promotion.objects.all()
    cart_count=0
    context={
        'types':types,
        'promotion':promotion,
        'cart_count':cart_count,
    }
    from django.template import loader
    temp = loader.get_template('index.html')
    static_html = temp.render(context)
    save_path = os.path.join(BASE_DIR, 'static/index.html')
    with open(save_path, 'w') as f:
        f.write(static_html)
