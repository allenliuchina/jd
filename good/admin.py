from django.contrib import admin
from .models import GoodType, Good, Promotion, GoodComment
from django.core.cache import cache
from .tasks import generate_index_html
from .tasks import create_new_good_cache, create_page_cache


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        generate_index_html.delay()  # 含有index_context缓存的更新
        create_new_good_cache.delay()
        create_page_cache.delay()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_index_html.delay()
        create_new_good_cache.delay()
        create_page_cache.delay()


class GoodAdmin(BaseAdmin):
    pass


class GoodTypeAdmin(BaseAdmin):
    pass


class PromotionAdmin(BaseAdmin):
    pass


class GoodCommentAdmin(admin.ModelAdmin):
    pass


admin.site.register(Good, GoodAdmin)
admin.site.register(GoodType, GoodTypeAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(GoodComment, GoodCommentAdmin)
