import pytest
from http import HTTPStatus

from pytest_django.asserts import assertRedirects, assertFormError
from django.urls import reverse

from news.models import Comment
from news.forms import BAD_WORDS, WARNING

pytestmark = pytest.mark.django_db


def test_user_can_create_comment(
        author_client,
        author,
        form_data,
        news,
        news_id
):
    url = reverse('news:detail', args=(news.id,))
    response = author_client.post(url, data=form_data)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 1
    comment = Comment.objects.get()
    assert comment.text == form_data['text']
    assert comment.author == author
    assert comment.news == news


@pytest.mark.django_db
def test_anonymous_user_cant_create_comment(client, form_data, news):
    url = reverse('news:detail', args=(news.id,))
    response = client.post(url, data=form_data)
    login_url = reverse('users:login')
    expected_url = f'{login_url}?next={url}'
    assertRedirects(response, expected_url)
    assert Comment.objects.count() == 0


def test_author_can_edit_comment(
        author_client,
        author,
        form_data,
        comment,
        news
):
    url = reverse('news:detail', args=(news.id,))
    edit_url = reverse('news:edit', args=(comment.id,))
    response = author_client.post((edit_url + '#comments'), form_data)
    assertRedirects(response, f'{url}#comments')
    comment.refresh_from_db()
    assert comment.text == form_data['text']
    assert comment.author == author


def test_author_can_delete_comment(author_client, author, comment, news):
    url = reverse('news:detail', args=(news.id,))
    delete_url = reverse('news:delete', args=(comment.id,))
    response = author_client.post(delete_url)
    assertRedirects(response, f'{url}#comments')
    assert Comment.objects.count() == 0


def test_other_user_cant_edit_comment(
        admin_client,
        author,
        form_data,
        comment,
        news
):
    edit_url = reverse('news:edit', args=(comment.id,))
    response = admin_client.post((edit_url + '#comments'), form_data)
    assert response.status_code == HTTPStatus.NOT_FOUND
    comment_from_db = Comment.objects.get(id=comment.id)
    assert comment.text == comment_from_db.text
    assert comment.author == comment_from_db.author


def test_other_user_cant_delete_comment(admin_client, author, comment, news):
    delete_url = reverse('news:delete', args=(comment.id,))
    response = admin_client.post(delete_url)
    assert response.status_code == HTTPStatus.NOT_FOUND
    assert Comment.objects.count() == 1


def test_user_cant_use_bad_words(
        author_client,
        author,
        form_data,
        news,
        news_id
):
    url = reverse('news:detail', args=(news.id,))
    bad_words_data = {'text': f'Какой-то текст, {BAD_WORDS[0]}, еще текст'}
    response = author_client.post(url, data=bad_words_data)
    assertFormError(response, 'form', 'text', errors=WARNING)
    assert Comment.objects.count() == 0
