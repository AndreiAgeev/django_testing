from notes.forms import NoteForm
from .common import TestCommon


class TestContent(TestCommon):
    """Класс для теста контента."""

    def test_auth_user_has_form_create_delete(self):
        """На страницах создания и редактирования заметки есть объект формы.

        Для авторизоавнного пользователя
        """
        urls = (self.add_url, self.edit_url)
        for url in urls:
            with self.subTest():
                response = self.author_client.get(url)
                self.assertIn('form', response.context)
                self.assertIsInstance(response.context['form'], NoteForm)

    def test_notes_list_for_different_users(self):
        """В списке одного пользователя нет заметок другого пользователя.

        Заметка передаётся в список, в словарь context.
        """
        users_statuses = (
            (self.author, True),
            (self.not_author, False)
        )
        for user, result in users_statuses:
            with self.subTest(user=user):
                self.client.force_login(user)
                response = self.client.get(self.list_url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, result)
