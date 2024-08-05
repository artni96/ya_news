import pytest

from news.models import News, Comment
from datetime import date, timedelta


@pytest.fixture
def author(django_user_model):
    author = django_user_model.objects.create(username='author')
    return author


@pytest.fixture
def author_client(author, client):
    client.force_login(author)
    return client


@pytest.fixture
def news():
    test_news = News.objects.create(
        title='тестовая новость',
        text='текст тестовой новости'
    )
    return test_news


@pytest.fixture
def news_for_main_page():
    for elem in range(11):
        News.objects.create(
            title=f'тестовая новость {elem}',
            text='текст тестовой новости',
            date=date.today() + timedelta(days=elem)
        )


@pytest.fixture
def comment(author, news):
    test_comment = Comment.objects.create(
        news=news,
        author=author,
        text='тестовый комментарий'
    )
    return test_comment


@pytest.fixture
def comments_for_news(author, news):
    for elem in range(5):
        Comment.objects.create(
            news=news,
            author=author,
            text=f'тестовый комментарий {elem}'
        )


@pytest.fixture
def news_id(news):
    return news.id


@pytest.fixture
def comment_id(comment):
    return comment.id


@pytest.fixture
def form_data(news_id, comment):
    return {
        'news': news_id,
        'text': 'Измененный комментарий',
        'author': comment.author
    }
