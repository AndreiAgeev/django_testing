from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestRoutes(TestCase):
    """Класс для теста маршрутов."""

    @classmethod
    def setUpTestData(cls):
        """Фикстуры класса TestRoutes."""
        cls.author = User.objects.create(username='Автор')
        cls.reader = User.objects.create(username='Не Автор')
        cls.note = Note.objects.create(
            title='Заметка',
            text='Текст заметки',
            slug='zametka',
            author=cls.author
        )

    def test_availability_for_note_view_edit_and_delete(self):
        """Доступность страниц просмотра/редактирования/удаления заметки.

        Для автора и другого авторизованного пользователя
        """
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.reader, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('notes:edit', 'notes:delete', 'notes:detail'):
                with self.subTest(user=user):
                    url = reverse(name, args=(self.note.slug,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_anon_redirects(self):
        """Проверка редиректов для анонимного юзера."""
        login_url = reverse('users:login')
        for name in (
            'notes:edit', 'notes:delete', 'notes:detail', 'notes:success',
            'notes:list'
        ):
            with self.subTest(name=name):
                if name in ('notes:success', 'notes:list'):
                    url = reverse(name)
                else:
                    url = reverse(name, args=(self.note.slug,))
                redirect_url = f'{login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_anon_user(self):
        """Проверка доступности страниц для анонимного пользователя.

        Проверяются следующие страницы: главная, страница новости, страница
        логина, страница разлогирования, страница регистрации.
        """
        for name in (
            'notes:home', 'users:login', 'users:logout', 'users:signup'
        ):
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Авторизованному пользователю доступны страницы списка заметок.

        добавления заметки, успешного добавления заметки
        """
        self.client.force_login(self.author)
        for name in ('notes:list', 'notes:add', 'notes:success'):
            with self.subTest():
                url = reverse(name)
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
