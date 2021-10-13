import pytest
from django.contrib.auth.models import User
from model_bakery import baker
from rest_framework.test import APIClient

from feed.models import Feed, FeedItem, UserFeedItem, UserFeedSubscription


@pytest.fixture
def user(db) -> User:
    return baker.make(
        User,
    )


@pytest.fixture
def api_client() -> APIClient:
    return APIClient()


@pytest.fixture
def user_api_client(user, api_client) -> APIClient:
    api_client.force_authenticate(user)
    return api_client


@pytest.fixture
def feed() -> Feed:
    return baker.make(
        Feed, name="test", url="http://www.kmGzSFDWeDtrBgpyvFpAdfKkbBCoxv.com/"
    )


@pytest.fixture
def feed_item(feed) -> FeedItem:
    return baker.make(FeedItem, feed=feed, title="test", description="dummy")


@pytest.fixture
def user_feed_subscription(user: User, feed: Feed) -> UserFeedSubscription:
    return baker.make(UserFeedSubscription, user=user, feeds=[feed])


@pytest.fixture
def user_feed_item(user: User, feed_item: FeedItem) -> UserFeedItem:
    return baker.make(UserFeedItem, user=user, feed=feed_item)
