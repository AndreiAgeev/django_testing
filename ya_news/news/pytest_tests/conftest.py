import pytest
from datetime import datetime, timedelta

from django.conf import settings
from django.test import Client
from django.utils import timezone

from news.models import Comment, News


@pytest.fixture
def news():
    return News.objects.create(title='Заголовок', text='Текст')


@pytest.fixture
def news_id(news):
    return (news.id,)


@pytest.fixture
def eleven_news():
    eleven_news = [
        News(
            title=f'Новость {index}',
            text='Текст',
            date=datetime.today() - timedelta(days=index)
        )
        for index in range(settings.NEWS_COUNT_ON_HOME_PAGE + 1)
    ]
    return News.objects.bulk_create(eleven_news)


@pytest.fixture
def author(django_user_model):
    return django_user_model.objects.create(username='Author')


@pytest.fixture
def not_author(django_user_model):
    return django_user_model.objects.create(username='Not author')


@pytest.fixture
def author_client(author):
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author):
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def comment(author, news):
    return Comment.objects.create(
        news=news,
        author=author,
        text='Текст'
    )


@pytest.fixture
def comment_id(comment):
    return (comment.id,)


@pytest.fixture
def many_comments(news, author):
    for i in range(5):
        comment = Comment.objects.create(
            news=news, author=author, text=f'Текст {i}'
        )
        comment.created = timezone.now() + timedelta(days=i)
        comment.save()


@pytest.fixture
def form_comment():
    return {'text': 'Комментарий'}
