from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note

User = get_user_model()


class TestSlug(TestCase):
    """Тесты для проверки параметра slug."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Фикстуры для TestSlug."""
        cls.user = User.objects.create(username='Автор')
        cls.user_client = Client()
        cls.user_client.force_login(cls.user)
        cls.note_title = 'Загоlovok/234'
        cls.create_url = reverse('notes:add')

    def test_title_to_slug(self):
        """Корректность преобразования title в slug при его незаполнении."""
        title_to_slug_form = {
            'title': self.note_title,
            'text': 'Текст',
            'author': self.user
        }
        response = self.user_client.post(
            self.create_url, data=title_to_slug_form
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Проверка корректности поля slug
        note = Note.objects.get()
        expected_slug = slugify(self.note_title)
        self.assertEqual(note.slug, expected_slug)

    def test_slug_duplicate(self):
        """Тест на ошибку создания заметки с существующим slug."""
        test_slug = 'test1'
        Note.objects.create(
            title='Заголовок',
            text='Текст',
            author=self.user,
            slug=test_slug
        )
        response = self.user_client.post(
            self.create_url,
            data={
                'title': 'Заголовок 2',
                'text': 'Текст',
                'author': self.user,
                'slug': test_slug
            }
        )
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=test_slug+WARNING
        )
        self.assertEqual(Note.objects.count(), 1)


class TestAnonymous(TestCase):
    """Тесты для анонимных пользователей."""

    @classmethod
    def setUpTestData(cls) -> None:
        """Фикстуры для TestAnonymous."""
        cls.create_url = reverse('notes:add')
        cls.form_data = {
            'title': 'Заголовок',
            'text': 'Текст',
        }

    def test_anon_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        response = self.client.post(self.create_url, data=self.form_data)
        login_url = reverse('users:login')
        expected_url = f'{login_url}?next={self.create_url}'
        notes_count = Note.objects.count()
        self.assertRedirects(response, expected_url)
        self.assertEqual(notes_count, 0)


class TestCreateEditDelete(TestCase):
    """Тесты для авторизованных пользователей."""

    NOTE_TEXT = 'Текст'
    NEW_NOTE_TEXT = 'Новый текст'
    NEW_TITLE = 'Заголовок2'

    @classmethod
    def setUpTestData(cls) -> None:
        """Фикстуры для TestCreateEditDelete."""
        cls.author = User.objects.create(username='Автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author = User.objects.create(username='Не автор')
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title='Заголовок',
            text=cls.NOTE_TEXT,
            author=cls.author,
            slug='note1'
        )
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.edit_form_data = {'title': 'Заголовок', 'text': cls.NEW_NOTE_TEXT}
        cls.new_form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_NOTE_TEXT}

    def test_user_cant_edit_others_note(self):
        """Проверка, что другие юзеры не могут редактичровать чужие заметки."""
        response = self.not_author_client.post(
            self.edit_url, data=self.edit_form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.note.refresh_from_db()
        self.assertEqual(self.note.text, self.NOTE_TEXT)

    def test_user_cant_delete_others_note(self):
        """Проверка, что другие юзеры не могут удалять чужие заметки."""
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверка, что автор может редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url, data=self.edit_form_data
        )
        self.note.refresh_from_db()
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(self.note.text, self.NEW_NOTE_TEXT)

    def test_author_can_delete_note(self):
        """Проверка, что автор может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, reverse('notes:success'))
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.not_author_client.post(
            reverse('notes:add'), data=self.new_form_data
        )
        self.assertRedirects(response, reverse('notes:success'))
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.NEW_TITLE)
        self.assertEqual(new_note.text, self.NEW_NOTE_TEXT)
        self.assertEqual(new_note.slug, slugify(self.NEW_TITLE))
        self.assertEqual(new_note.author, self.not_author)
