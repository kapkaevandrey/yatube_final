from django.core.paginator import Paginator, Page
from django.conf import settings


def _get_pages(request, page_list: object) -> Page:
    paginator = Paginator(page_list, settings.PAGINATOR_PAGE_NUM)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)