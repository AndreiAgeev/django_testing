from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from notes.models import Note

User = get_user_model()


class TestCommon(TestCase):
    """Базовый класс для тестов."""
    TITLE = 'Заголовок'
    NEW_TITLE = 'Новый заголовок'
    TEXT = 'Текст'
    NEW_TEXT = 'Новый текст'
    SLUG = 'note1'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = User.objects.create(username='Автор')
        cls.not_author = User.objects.create(username='Не автор')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.not_author_client = Client()
        cls.not_author_client.force_login(cls.not_author)
        cls.note = Note.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
            author=cls.author,
            slug=cls.SLUG
        )
        cls.home_url = reverse('notes:home')
        cls.add_url = reverse('notes:add')
        cls.edit_url = reverse('notes:edit', args=(cls.note.slug,))
        cls.delete_url = reverse('notes:delete', args=(cls.note.slug,))
        cls.detail_url = reverse('notes:detail', args=(cls.note.slug,))
        cls.list_url = reverse('notes:list')
        cls.success_url = reverse('notes:success')
        cls.login_url = reverse('users:login')
        cls.logout_url = reverse('users:logout')
        cls.signup_url = reverse('users:signup')
        cls.form_data = {'title': cls.NEW_TITLE, 'text': cls.NEW_TEXT}
