from unittest import skip

from django.test import TestCase

from news.models import News


@skip('Эти тесты для примера')
class TestNews(TestCase):

    TITLE = 'Заголовок новости'
    TEXT = 'Тестовый текст'

    @classmethod
    def setUpTestData(cls) -> None:
        cls.news = News.objects.create(
            title=cls.TITLE,
            text=cls.TEXT,
        )

    def test_successful_creation(self):
        self.assertEqual(News.objects.count(), 1)

    def test_title(self):
        self.assertEqual(self.news.title, self.TITLE)
