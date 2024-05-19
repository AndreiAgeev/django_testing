from http import HTTPStatus

from .common import TestCommon


class TestRoutes(TestCommon):
    """Класс для теста маршрутов."""

    def test_availability_for_note_view_edit_and_delete(self):
        """Доступность страниц просмотра/редактирования/удаления заметки.

        Для автора и другого авторизованного пользователя
        """
        urls = (self.edit_url, self.delete_url, self.detail_url)
        users_statuses = (
            (self.author, HTTPStatus.OK),
            (self.not_author, HTTPStatus.NOT_FOUND)
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for url in urls:
                with self.subTest(user=user):
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_anon_redirects(self):
        """Проверка редиректов для анонимного юзера."""
        urls = (
            self.edit_url, self.delete_url, self.detail_url,
            self.success_url, self.list_url
        )
        for url in urls:
            with self.subTest(url=url):
                redirect_url = f'{self.login_url}?next={url}'
                response = self.client.get(url)
                self.assertRedirects(response, redirect_url)

    def test_availability_for_anon_user(self):
        """Проверка доступности страниц для анонимного пользователя.

        Проверяются следующие страницы: главная, страница новости, страница
        логина, страница разлогирования, страница регистрации.
        """
        urls = (
            self.home_url, self.login_url, self.logout_url, self.signup_url
        )
        for url in urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_availability_for_auth_user(self):
        """Авторизованному пользователю доступны страницы списка заметок.

        добавления заметки, успешного добавления заметки
        """
        urls = (self.list_url, self.add_url, self.success_url)
        for url in urls:
            with self.subTest(url=url):
                response = self.author_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)
