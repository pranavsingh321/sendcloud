from unittest.mock import patch

import pytest
from rest_framework.exceptions import APIException

from feed.models import FeedItem
from feed.tasks import fetch_feed_sub_task, fetch_feeds_task
from feed.tests.data_dump import ALGEMEEN, FEEDBURNER


@pytest.mark.django_db
@patch("feed.tasks.fetch_feed_sub_task.apply_async")
def test_feed_list_fetch(mock_fetch, feed):
    fetch_feeds_task()
    mock_fetch.assert_called_with(args=(feed.id,))


@pytest.mark.django_db
@pytest.mark.parametrize(
    ("url", "api_return", "title"),
    (
        ("http://www.nu.nl/rss/Algemeen", ALGEMEEN, "Zeker"),
        ("https://feeds.feedburner.com/tweakers/mixed", FEEDBURNER, "Asustor"),
    ),
)
@patch("feed.feed_parser.Parser._fetch_data")
def test_fetch_feed_sub_task(mock_api_call, url, api_return, title, feed):
    mock_api_call.return_value = api_return
    fetch_feed_sub_task(feed.id)
    assert FeedItem.objects.count() == 1
    assert [
        feeditem for feeditem in FeedItem.objects.values("title", "feed_id")
    ] == [{"title": title, "feed_id": feed.id}]


@patch("feed.tasks.send_mail_user.apply")
def test_api_failure(send_mail_user_mock, user, feed, user_feed_subscription):
    exc = APIException("Test")
    task_id = "fetch_feed_sub_task_id"
    args = [feed.id]
    kwargs = {}
    einfo = None

    fetch_feed_sub_task.on_failure(exc, task_id, args, kwargs, einfo)
    send_mail_user_mock.assert_called_with(args=(user.id, feed.name))
