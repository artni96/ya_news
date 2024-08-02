import pytest

from news.models import News, Comment


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
def comment(author, news):
    test_comment = Comment.objects.create(
        news=news,
        author=author,
        text='тестовый комментарий'
    )
    return test_comment


@pytest.fixture
def news_id(news):
    return news.id


@pytest.fixture
def comment_id(comment):
    return comment.id
