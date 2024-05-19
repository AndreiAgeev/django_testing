import pytest
from django.conf import settings
from django.urls import reverse

from news.forms import CommentForm

author_client = pytest.lazy_fixture('author_client')
client = pytest.lazy_fixture('client')


@pytest.mark.usefixtures('many_news')
def test_news_count(client):
    """Тест корректности отображения нужного кол-ва новостей на главной"""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert object_list.count() == settings.NEWS_COUNT_ON_HOME_PAGE


@pytest.mark.usefixtures('many_news')
def test_news_order(client):
    """Тест корректной сортировки новостей"""
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    all_dates = [news.date for news in object_list]
    expected_dates = sorted(all_dates, reverse=True)
    assert all_dates == expected_dates


@pytest.mark.usefixtures('many_comments')
def test_comment_order(client, news_id):
    """Тест корректной сортировки комментариев"""
    url = reverse('news:detail', args=news_id)
    response = client.get(url)
    assert 'news' in response.context
    news = response.context['news']
    all_comments = news.comment_set.all()
    all_timestamps = [comment.created for comment in all_comments]
    expected_reslut = sorted(all_timestamps)
    assert all_timestamps == expected_reslut


@pytest.mark.parametrize(
    'user_client, result',
    (
        (author_client, True),
        (client, False)
    )
)
def test_detail_page_has_comment_form(user_client, result, news_id):
    """Тест корректности отображения формы комментариев.

    В зависимости от пользователя
    """
    url = reverse('news:detail', args=news_id)
    response = user_client.get(url)
    if result:
        assert 'form' in response.context
        assert isinstance(response.context['form'], CommentForm)
    else:
        assert 'form' not in response.context
