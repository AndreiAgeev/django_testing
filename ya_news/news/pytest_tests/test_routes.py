import pytest
from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects


@pytest.mark.django_db
@pytest.mark.parametrize(
    'name, id',
    (
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id')),
        ('users:login', None),
        ('users:logout', None),
        ('users:signup', None),
    )
)
def test_availability_for_anon_user(client, name, id):
    """Проверка доступности страниц для анонимного пользователя.

    Проверяются следующие страницы: главная, страница новости, страница логина,
    страница разлогирования, страница регистрации.
    """
    url = reverse(name, args=id)
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'user_client, expected_result',
    (
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK),
        (pytest.lazy_fixture('not_author_client'), HTTPStatus.NOT_FOUND)
    )
)
@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
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


@pytest.mark.parametrize(
    'name, args',
    (
        ('news:edit', pytest.lazy_fixture('comment_id')),
        ('news:delete', pytest.lazy_fixture('comment_id')),
    )
)
def test_redirect_for_anon_client(client, name, args):
    """Тест доступности страниц редактирования и удаления комментариев.

    Для незарегистрированного пользователя
    """
    login_url = reverse('users:login')
    url = reverse(name, args=args)
    response = client.get(url)
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
