from django.contrib import admin
from .models import GoodType, Good, Promotion, GoodComment

from .tasks import generate_index_html


class BaseAdmin(admin.ModelAdmin):
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        generate_index_html.delay()

    def delete_model(self, request, obj):
        super().delete_model(request, obj)
        generate_index_html.delay()


class GoodAdmin(BaseAdmin):
    pass


class GoodTypeAdmin(BaseAdmin):
    pass


class PromotionAdmin(BaseAdmin):
    pass


class GoodCommentAdmin(BaseAdmin):
    pass


admin.site.register(Good, GoodAdmin)
admin.site.register(GoodType, GoodTypeAdmin)
admin.site.register(Promotion, PromotionAdmin)
admin.site.register(GoodComment, GoodCommentAdmin)
