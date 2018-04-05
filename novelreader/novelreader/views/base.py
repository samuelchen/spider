from django.views.generic.base import ContextMixin
from django.conf import settings
__author__ = 'samuel'


class BaseViewMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseViewMixin, self).get_context_data(**kwargs)
        context['website'] = settings.WEBSITE

        return context

    def gen_pager_context(self, context, items, page_items=settings.ITEMS_PER_PAGE):
        page = int(self.request.GET.get('p', 0))
        if page > 0:
            context['pp'] = page - 1
        if len(items) >= page_items:
            context['np'] = page + 1