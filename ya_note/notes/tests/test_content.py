from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from notes.forms import NoteForm
from notes.models import Note

User = get_user_model()


class TestContent(TestCase):
    """Класс для теста контента."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Фикстуры для клосса TestContent."""
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.note = Note.objects.create(
            title='Заголовок',
            text='Текст',
            slug='zagolovok',
            author=cls.author
        )
        cls.note_edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.note_create_url = reverse('notes:add')

    def test_auth_user_has_form_create_delete(self):
        """На страницах создания и редактирования заметки есть объект формы.

        Для авторизоавнного пользователя
        """
        self.client.force_login(self.author)
        for url in (self.note_create_url, self.note_edit_url):
            with self.subTest():
                response = self.client.get(url)
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
        url = reverse('notes:list')
        for user, result in users_statuses:
            with self.subTest():
                self.client.force_login(user)
                response = self.client.get(url)
                object_list = response.context['object_list']
                self.assertIs(self.note in object_list, result)
