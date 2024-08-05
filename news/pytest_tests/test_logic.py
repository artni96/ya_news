from http import HTTPStatus

import pytest
from django.urls import reverse
from pytest_django import asserts

from news.models import Comment
from news.forms import WARNING


@pytest.mark.django_db
@pytest.mark.parametrize(
    'test_client, comments_amount',
    [
        (pytest.lazy_fixture('client'), 1),
        (pytest.lazy_fixture('author_client'), 2)
    ]
)
def test_comment_creation_by_users(
    form_data, test_client, comments_amount, news
):
    url = reverse('news:detail', kwargs={
        'pk': news.id
    })
    test_client.post(url, data=form_data)
    assert Comment.objects.count() == comments_amount


@pytest.mark.django_db
def test_author_can_delete_comment(author_client, comment_id, comment):
    url = reverse('news:delete', kwargs={
        'pk': comment_id
    })
    response = author_client.post(url)
    redirect_url = f'/news/{comment.news.id}/#comments'
    asserts.assertRedirects(response, redirect_url)
    assert Comment.objects.count() == 0


@pytest.mark.django_db
def test_others_cant_delete_comment(admin_client, comment_id, comment):
    url = reverse('news:delete', kwargs={
        'pk': comment_id
    })
    response = admin_client.post(url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


@pytest.mark.django_db
def test_author_can_edit_comment(
    author_client, comment_id, form_data, comment
):
    url = reverse('news:edit', kwargs={
        'pk': comment_id
    })
    response = author_client.post(url, data=form_data)
    redirect_url = f'/news/{comment.news.id}/#comments'
    asserts.assertRedirects(response, redirect_url)
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.news.id == form_data['news']
    assert comment.author == form_data['author']


@pytest.mark.django_db
def test_others_cant_edit_comment(
    admin_client, comment_id, form_data, comment
):
    url = reverse('news:edit', kwargs={
        'pk': comment_id
    })
    response = admin_client.post(url, data=form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment.refresh_from_db()
    db_comment = Comment.objects.get(id=comment_id)
    assert comment.text == db_comment.text
    assert comment.news.id == db_comment.news.id
    assert comment.author == db_comment.author


@pytest.mark.django_db
def test_insulting_words_cant_be_used(form_data, comment_id, author_client):
    form_data['text'] = 'редиска'
    url = reverse('news:detail', kwargs={
        'pk': comment_id
    })
    response = author_client.post(url, data=form_data)
    asserts.assertFormError(
        response, 'form', 'text', errors=(WARNING))
