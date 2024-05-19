from http import HTTPStatus

from pytils.translit import slugify

from notes.forms import WARNING
from notes.models import Note
from .common import TestCommon


class TestSlug(TestCommon):
    """Тесты для проверки параметра slug."""

    def test_title_to_slug(self):
        """Корректность преобразования title в slug при его незаполнении."""
        # Для чистоты теста удаляем заметку, созданную в фикстуре
        Note.objects.all().delete()
        # Посылаем запрос на создание новой заметки без поля slug
        response = self.author_client.post(
            self.add_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        # Проверка корректности поля slug
        note = Note.objects.get()
        expected_slug = slugify(self.form_data['title'])
        self.assertEqual(note.slug, expected_slug)

    def test_slug_duplicate(self):
        """Тест на ошибку создания заметки с существующим slug."""
        self.form_data['slug'] = self.SLUG
        response = self.author_client.post(self.add_url, data=self.form_data)
        self.assertFormError(
            response,
            form='form',
            field='slug',
            errors=self.SLUG + WARNING
        )
        self.assertEqual(Note.objects.count(), 1)


class TestAnonymous(TestCommon):
    """Тесты для анонимных пользователей."""

    def test_anon_cant_create_note(self):
        """Анонимный пользователь не может создать заметку."""
        # Удаляем заметку, созданную в фикстуре
        Note.objects.all().delete()
        response = self.client.post(self.add_url, data=self.form_data)
        expected_url = f'{self.login_url}?next={self.add_url}'
        self.assertRedirects(response, expected_url)
        self.assertEqual(Note.objects.count(), 0)


class TestCreateEditDelete(TestCommon):
    """Тесты для авторизованных пользователей."""

    def test_user_cant_edit_others_note(self):
        """Проверка, что другие юзеры не могут редактичровать чужие заметки."""
        response = self.not_author_client.post(
            self.edit_url, data=self.form_data
        )
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        new_note = Note.objects.get()
        self.assertEqual(self.note.text, new_note.text)

    def test_user_cant_delete_others_note(self):
        """Проверка, что другие юзеры не могут удалять чужие заметки."""
        response = self.not_author_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.assertEqual(Note.objects.count(), 1)

    def test_author_can_edit_note(self):
        """Проверка, что автор может редактировать свои заметки."""
        response = self.author_client.post(
            self.edit_url, data=self.form_data
        )
        new_note = Note.objects.get()
        self.assertRedirects(response, self.success_url)
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.title, self.form_data['title'])

    def test_author_can_delete_note(self):
        """Проверка, что автор может удалять свои заметки."""
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.success_url)
        self.assertEqual(Note.objects.count(), 0)

    def test_user_can_create_note(self):
        """Авторизованный пользователь может создать заметку."""
        response = self.not_author_client.post(
            self.add_url, data=self.form_data
        )
        self.assertRedirects(response, self.success_url)
        new_note = Note.objects.last()
        self.assertEqual(new_note.title, self.form_data['title'])
        self.assertEqual(new_note.text, self.form_data['text'])
        self.assertEqual(new_note.slug, slugify(self.form_data['title']))
        self.assertEqual(new_note.author, self.not_author)
