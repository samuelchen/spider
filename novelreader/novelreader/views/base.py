from django.views.generic.base import ContextMixin
from django.conf import settings
__author__ = 'samuel'


class BaseViewMixin(ContextMixin):

    def get_context_data(self, **kwargs):
        context = super(BaseViewMixin, self).get_context_data(**kwargs)
        context['website'] = settings.WEBSITE

        return context