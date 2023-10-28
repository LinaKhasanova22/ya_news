import pytest

from django.urls import reverse

from yanews.settings import NEWS_COUNT_ON_HOME_PAGE

pytestmark = pytest.mark.django_db


def test_news_count(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    news_count = len(object_list)
    assert news_count == NEWS_COUNT_ON_HOME_PAGE


def test_news_order(client, all_news):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    sorted_dates = sorted(all_dates, reverse=True)
    assert all_dates == sorted_dates


def test_comments_order(client, news, comment_count):
    url = reverse('news:detail', args=(news.id,))
    response = client.get(url)
    news = response.context['news']
    assert 'news' in response.context
    all_comments = news.comment_set.all()
    assert all_comments[0].created < all_comments[1].created


@pytest.mark.parametrize(
    'parametrized_client, form_exist',
    (
        (pytest.lazy_fixture('admin_client'), True),
        (pytest.lazy_fixture('client'), False),
    )
)
def test_pages_contains_form(parametrized_client, form_exist, news):
    url = reverse('news:detail', args=(news.id,))
    response = parametrized_client.get(url)
    assert ('form' in response.context) is form_exist
