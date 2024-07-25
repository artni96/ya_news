from datetime import date
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from news.models import Comment, News

User = get_user_model()


class TestNews(TestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.test_user_1 = User.objects.create(username='test_user_1')
        cls.test_user_2 = User.objects.create(username='test_user_2')
        cls.user_client_1 = Client()
        cls.user_client_2 = Client()
        cls.anonymous_client = Client()
        cls.user_client_1.force_login(cls.test_user_1)
        cls.user_client_2.force_login(cls.test_user_2)
        cls.test_news = News.objects.create(
            title='Тестовая новость',
            text='Текстовый текст тестовой новости',
            date=date.today()
        )
        cls.test_comment = Comment.objects.create(
            news=cls.test_news,
            author=cls.test_user_1,
            text='тестовый комментарий'
        )

    # мой вариант
    def test_modify_exact_comment_by_author(self):
        url = reverse('news:edit', kwargs={
            'pk': self.test_comment.id
        })
        url_tuple = (
            ('news:edit', (self.test_comment.id,)),
            ('news:delete', (self.test_comment.id,)),
        )
        for url, args in url_tuple:
            with self.subTest(url=url):
                response = self.user_client_1.get(reverse(url, args=args))
                self.assertEqual(response.status_code, HTTPStatus.OK)

    # мой вариант
    def test_modify_comment_by_anonym(self):
        def get_url(self, url):
            return reverse(
                url,
                kwargs={'pk': self.test_comment.id})
        url = reverse('news:edit', kwargs={
            'pk': self.test_comment.id
        })

        login_url = reverse('users:login')
        for url in ('news:edit', 'news:delete'):
            with self.subTest(url=url):
                test_url = get_url(self, url)
                redirect_url = f'{login_url}?next={test_url}'
                response = self.anonymous_client.get(test_url)
                self.assertRedirects(response, redirect_url)

    # вариант ЯП
    def test_availability_for_comment_edit_and_delete(self):
        users_statuses = (
            (self.test_user_1, HTTPStatus.OK),
            (self.test_user_2, HTTPStatus.NOT_FOUND),
        )
        for user, status in users_statuses:
            self.client.force_login(user)
            for name in ('news:edit', 'news:delete'):
                with self.subTest(user=user, name=name):
                    url = reverse(name, args=(self.test_comment.id,))
                    response = self.client.get(url)
                    self.assertEqual(response.status_code, status)

    def test_edit_exact_comment_not_by_author(self):
        url = reverse('news:edit', kwargs={'pk': self.test_comment.id})
        response = self.user_client_2.get(url)
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_by_anonym(self):
        urls_tuple = (
            ('users:signup', None),
            ('users:login', None),
            ('users:logout', None),
            ('news:home', None),
            ('news:detail', (self.test_news.id,))
        )
        for url, argument in urls_tuple:
            with self.subTest(url=url):
                response = self.anonymous_client.get(
                    reverse(url, args=argument)
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)
