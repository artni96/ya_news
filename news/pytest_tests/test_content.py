import pytest

from django.urls import reverse


@pytest.mark.django_db
def test_note_in_list_for_all_users(news, client):
    url = reverse('news:home')
    response = client.get(url)
    assert news in response.context['object_list']


@pytest.mark.parametrize(
    'test_client, status',
    (
        (pytest.lazy_fixture('author_client'), True),
        (pytest.lazy_fixture('client'), False)
    )
)
@pytest.mark.django_db
def test_comment_creation_form_for_different_users(
    test_client, status, news_id
):
    url = reverse('news:detail', kwargs={
        'pk': news_id
    })
    response = test_client.get(url)
    assert ('form' in response.context) is status


@pytest.mark.django_db
def test_comment_can_be_seen_on_news_page(
    author_client, news_id, comment, comments_for_news
):
    url = reverse('news:detail', kwargs={
        'pk': news_id
    })
    response = author_client.get(url)
    obj = response.context['object']
    assert obj.comment_set.first().text == comment.text
    assert (
        obj.comment_set.get(id=1).created
        < obj.comment_set.get(id=2).created
        < obj.comment_set.get(id=3).created
    )


@pytest.mark.django_db
def test_news_order(client, news_for_main_page):
    url = reverse('news:home')
    response = client.get(url)
    object_list = response.context['object_list']
    assert len(response.context['object_list']) == 10
    assert object_list[0].date > object_list[1].date > object_list[9].date
