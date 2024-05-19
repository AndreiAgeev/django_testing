from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django.asserts import assertRedirects

news_id = pytest.lazy_fixture('news_id')
author_client = pytest.lazy_fixture('author_client')
not_author_client = pytest.lazy_fixture('not_author_client')
comment_id = pytest.lazy_fixture('comment_id')


@pytest.mark.parametrize(
    'name, object_id',
    (
        ('news:home', None),
        ('news:detail', news_id),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
        ('news:edit', comment_id),
        ('news:delete', comment_id),
    )
)
def test_availability_for_anon_user(client, name, object_id):
    """Проверка доступности страниц и редиректов для анонимного пользователя.

    Проверяются следующие страницы: главная, страница новости, страница логина,
    страница разлогирования, страница регистрации.
    """
    url = reverse(name, args=object_id)
    response = client.get(url)
    if name in ('news:edit', 'news:delete'):
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={url}'
        assertRedirects(response, expected_url)
    else:
        assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user_client, expected_result',
    (
        (author_client, HTTPStatus.OK),
        (not_author_client, HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', comment_id),
        ('news:delete', comment_id),
    )
)
def test_availability_for_comment_edit_and_delete(
    user_client, expected_result, name, args
):
    """Тест доступности страниц редактирования и удаления комментариев.

    Для автора и не автора
    """
    url = reverse(name, args=args)
    response = user_client.get(url)
    assert response.status_code == expected_result
