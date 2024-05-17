import pytest

from http import HTTPStatus

from django.urls import reverse
from pytest_django.asserts import assertRedirects, assertFormError

from news.forms import WARNING
from news.models import Comment


@pytest.mark.django_db
@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
def test_comment_creation(user_client, result, news_id, form_comment, author):
    """Проверка возможности создания комментариев.

    Для анонимных и авторизованных юзеров
    """
    url = reverse('news:detail', args=(news_id))
    response = user_client.post(url, data=form_comment)
    if result:
        assertRedirects(response, f'{url}#comments')
        assert Comment.objects.count() == 1
        comment = Comment.objects.get()
        assert comment.text == form_comment['text']
        assert comment.author == author
        assert comment.news.id == news_id[0]
    else:
        assert Comment.objects.count() == 0


def test_user_cant_use_bad_words(author_client, news_id, form_comment):
    """Проверка невозможности создания комментариев с запрещёнными словами"""
    url = reverse('news:detail', args=news_id)
    form_comment['text'] = 'В комментарии есть редиска'
    response = author_client.post(url, data=form_comment)
    assertFormError(response, 'form', 'text', WARNING)
    assert Comment.objects.count() == 0


@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False)
    )
)
def test_delete_comment(user_client, result, news_id, comment_id):
    """Проверка возможности удаления комментариев разными юзерами"""
    url = reverse('news:delete', args=comment_id)
    response = user_client.delete(url)
    if result:
        assertRedirects(
            response, reverse('news:detail', args=news_id) + '#comments'
        )
        assert Comment.objects.count() == 0
    else:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert Comment.objects.count() == 1


@pytest.mark.parametrize(
    'user_client, result',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('not_author_client'), False)
    )
)
def test_edit_comment(user_client, result, news_id, comment, form_comment):
    """Проверка возможности редактирования комментариев разными юзерами"""
    url = reverse('news:edit', args=(comment.id,))
    old_comment_text = comment.text
    response = user_client.post(url, data=form_comment)
    comment.refresh_from_db()
    if result:
        assertRedirects(
            response, reverse('news:detail', args=news_id) + '#comments'
        )
        assert comment.text == form_comment['text']
    else:
        assert response.status_code == HTTPStatus.NOT_FOUND
        assert comment.text == old_comment_text
