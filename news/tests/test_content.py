from datetime import date, timedelta

from django.conf import settings
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.utils import timezone

from news.models import Comment, News

User = get_user_model()


class TestContent(TestCase):

    @classmethod
    def setUpTestData(cls):
        News.objects.bulk_create([
            News(
                title=f'Новость {i}',
                text=f'Текст для новости {i}',
                date=date.today() + timedelta(days=i)
            ) for i in range(
                settings.NEWS_COUNT_ON_HOME_PAGE + 1)])
        cls.HOME_PAGE_URL = 'news:home'
        cls.author = User.objects.create(username='author')
        cls.author_client = Client()
        cls.author_client.force_login(cls.author)
        cls.test_news = News.objects.first()
        cls.EXACT_NEWS_PAGE_URL = ('news:detail', cls.test_news.id)
        for i in range(5):
            comment = Comment.objects.create(
                news=cls.test_news,
                author=cls.author,
                text=f'Комментарий {i}',
            )
            comment.created = timezone.now() + timedelta(hours=i)
            comment.save()

    def test_amount_news(self):
        response = self.client.get(reverse(self.HOME_PAGE_URL))
        self.assertEqual(
            response.context['object_list'].count(),
            settings.NEWS_COUNT_ON_HOME_PAGE
        )

    # вариант ЯП
    def test_news_order(self):
        response = self.client.get(reverse(self.HOME_PAGE_URL))
        object_list = response.context['object_list']
        all_dates = [news.date for news in object_list]
        sorted_dates = sorted(all_dates, reverse=True)
        self.assertEqual(all_dates, sorted_dates)

    # мой вариант
    def test_news_ordering(self):
        response = self.client.get(reverse(self.HOME_PAGE_URL))
        test_news_date_list = [
            news.date for news in response.context['object_list']
        ]
        sorted_list = sorted(test_news_date_list, reverse=True)
        self.assertEqual(test_news_date_list, sorted_list)

    # мой вариант
    def test_comments_ordering(self):
        response = self.client.get(
            reverse(
                self.EXACT_NEWS_PAGE_URL[0],
                args=(self.EXACT_NEWS_PAGE_URL[1],)
            )
        )
        news_comments_time_creation = [
            comment.created for comment in
            response.context['object'].comment_set.all()
        ]
        # pp(news_comments_time_creation)
        self.assertEqual(
            news_comments_time_creation,
            sorted(news_comments_time_creation)
        )

    # вариант ЯП
    def test_comments_order(self):
        response = self.client.get(
            reverse(
                self.EXACT_NEWS_PAGE_URL[0],
                args=(self.EXACT_NEWS_PAGE_URL[1],)
            )
        )
        self.assertIn('news', response.context)
        news = response.context['news']
        all_comments = news.comment_set.all()
        self.assertLess(all_comments[0].created, all_comments[1].created)

    def test_anonymous_client_has_no_form(self):
        response = self.client.get(
            reverse(
                self.EXACT_NEWS_PAGE_URL[0],
                args=(self.EXACT_NEWS_PAGE_URL[1],)
            )
        )
        self.assertNotIn('form', response.context)

    def test_authorized_client_has_form(self):
        response = self.author_client.get(
            reverse(
                self.EXACT_NEWS_PAGE_URL[0],
                args=(self.EXACT_NEWS_PAGE_URL[1],)
            )
        )
        self.assertIn('form', response.context)
