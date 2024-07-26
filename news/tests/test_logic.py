from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.urls import reverse

from news.models import Comment, News


User = get_user_model()


class TestCommentCreation(TestCase):
    COMMENT_TEXT = 'текст комментария'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        cls.url = reverse('news:detail', args=(cls.news.pk,))
        cls.user = User.objects.create(username='test_user')
        cls.auth_client = Client()
        cls.auth_client.force_login(cls.user)
        cls.form_data = {'text': cls.COMMENT_TEXT}

    def test_anonymous_user_cant_create_comment(self):
        self.client.post(self.url, data=self.form_data)
        comment_count = Comment.objects.count()
        self.assertEqual(comment_count, 0)

    def test_auth_user_can_creat_comment(self):
        self.auth_client.post(self.url, data=self.form_data)
        comment_count = self.user.comment_set.count()
        self.assertEqual(comment_count, 1)
        comment = self.user.comment_set.first()
        print(comment)
        self.assertEqual(comment.text, self.COMMENT_TEXT)
        self.assertEqual(comment.news.text, self.news.text)
        self.assertEqual(comment.news.title, self.news.title)
        self.assertEqual(comment.author, self.user)

    def test_user_cant_use_bad_words(self):
        BAD_WORDS = ['редиска',]
        bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
        response = self.auth_client.post(self.url, data=bad_words_data)
        self.assertFormError(
            response,
            form='form',
            field='text',
            errors='Использование апрещенных слов'
        )
        comments_count = Comment.objects.count()
        self.assertEqual(comments_count, 0)


class TestCommentEditDelete(TestCase):
    # Тексты для комментариев не нужно дополнительно создавать
    # (в отличие от объектов в БД), им не нужны ссылки на self или cls,
    # поэтому их можно перечислить просто в атрибутах класса.
    COMMENT_TEXT = 'Текст комментария'
    NEW_COMMENT_TEXT = 'Обновлённый комментарий'

    @classmethod
    def setUpTestData(cls):
        cls.news = News.objects.create(title='Заголовок', text='Текст')
        news_url = reverse('news:detail', args=(cls.news.id,))
        cls.url_to_comments = news_url + '#comments'
        cls.author = User.objects.create(username='Автор комментария')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.reader = User.objects.create(username='Читатель')
        cls.reader_client = Client()
        cls.reader_client.force_login(cls.reader)
        cls.comment = Comment.objects.create(
            news=cls.news,
            author=cls.author,
            text=cls.COMMENT_TEXT
        )
        cls.edit_url = reverse('news:edit', args=(cls.comment.id,))
        cls.delete_url = reverse('news:delete', args=(cls.comment.id,))
        cls.form_data = {'text': cls.NEW_COMMENT_TEXT}

    def test_author_can_delete_comment(self):
        response = self.author_client.delete(self.delete_url)
        self.assertRedirects(response, self.url_to_comments)
        comments_count = self.author.comment_set.count()
        self.assertEqual(comments_count, 0)

    def test_user_cant_delete_comment_of_another_user(self):
        response = self.reader_client.delete(self.delete_url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        comments_count = self.author.comment_set.count()
        self.assertEqual(comments_count, 1)

    def test_author_can_edit_comment(self):
        response = self.author_client.post(self.edit_url, data=self.form_data)
        self.assertRedirects(response, self.url_to_comments)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.NEW_COMMENT_TEXT)

    def test_user_cant_edit_comment_of_another_user(self):
        response = self.reader_client.post(self.edit_url, data=self.form_data)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
        self.comment.refresh_from_db()
        self.assertEqual(self.comment.text, self.COMMENT_TEXT)
        self.assertNotEqual(self.comment.text, self.NEW_COMMENT_TEXT)
