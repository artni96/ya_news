from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django import asserts


@pytest.mark.django_db
@pytest.mark.parametrize(
    'url, pk', [
        ('users:signup', None),
        ('users:login', None),
        ('users:logout', None),
        ('news:home', None),
        ('news:detail', pytest.lazy_fixture('news_id'))
    ]
)
def test_pages_by_anonymous_user(client, url, pk):
    if not pk:
        url = reverse(url)
    else:
        url = reverse(url, kwargs={
            'pk': pk
        })
    response = client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, pk', [
        ('news:delete', pytest.lazy_fixture('comment_id')),
        ('news:edit', pytest.lazy_fixture('comment_id'))
    ]
)
def test_comments_by_author(author_client, url, pk):
    url = reverse(url, kwargs={
        'pk': pk
    })
    response = author_client.get(url)
    assert response.status_code == HTTPStatus.OK


@pytest.mark.parametrize(
    'url, pk', [
        ('news:delete', pytest.lazy_fixture('comment_id')),
        ('news:edit', pytest.lazy_fixture('comment_id'))
    ]
)
def test_redirect_for_unauthorized_users(client, pk, url, comment_id):
    url = reverse(url, kwargs={
        'pk': pk
    })
    response = client.get(url)
    redirect_url = f'{reverse("users:login")}?next={url}'
    asserts.assertRedirects(response, redirect_url)


@pytest.mark.parametrize(
    'url, pk', [
        ('news:delete', pytest.lazy_fixture('comment_id')),
        ('news:edit', pytest.lazy_fixture('comment_id'))
    ]
)
def test_others_cant_edit_or_delete_comment(admin_client, pk, url):
    url = reverse(url, kwargs={
        'pk': pk
    })
    response = admin_client.get(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
