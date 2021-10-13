from unittest.mock import patch

import pytest
from model_bakery import baker

from feed.models import FeedItem, UserFeedSubscription
from feed.tests.data_dump import ALGEMEEN


def test_feed_list_fetch(user_api_client, feed):
    response = user_api_client.get("/feed/feed/?format=json", format="json")
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"] == [
        {"id": feed.id, "url": feed.url, "name": feed.name}
    ]


def test_feed_detail_fetch(user_api_client, feed):
    response = user_api_client.get(
        f"/feed/feed/{feed.id}/?format=json", format="json"
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": feed.id,
        "url": feed.url,
        "name": feed.name,
    }


def test_feed_item_list_for_user(
    user, user_api_client, feed_item, user_feed_subscription
):
    response = user_api_client.get(
        "/feed/feed-item/?format=json", format="json"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"] == [
        {
            "id": feed_item.id,
            "feed": feed_item.feed.id,
            "title": feed_item.title,
            "description": feed_item.description,
            "has_read": False,
        }
    ]


def test_feed_item_list_for_user_without_subscription(
    user_api_client, feed_item
):
    response = user_api_client.get(
        "/feed/feed-item/?format=json", format="json"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 0


def test_feed_item_detail_for_user(
    user_api_client, feed_item, user_feed_subscription
):
    response = user_api_client.get(
        f"/feed/feed-item/{feed_item.id}/?format=json", format="json"
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": feed_item.id,
        "feed": feed_item.feed.id,
        "title": feed_item.title,
        "description": feed_item.description,
        "has_read": False,
    }


def test_feed_filter_on_feed_items_list(
    user_api_client, user, feed_item, user_feed_subscription
):
    name = "test title"
    feed_item_2 = baker.make(FeedItem, title=name, feed__name="dummy")
    baker.make(UserFeedSubscription, user=user, feeds=[feed_item_2.feed])
    response = user_api_client.get(
        "/feed/feed-item/?feed=dummy&format=json", format="json"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 1
    assert data["results"] == [
        {
            "id": feed_item_2.id,
            "feed": feed_item_2.feed.id,
            "title": name,
            "description": feed_item_2.description,
            "has_read": False,
        }
    ]


def test_feed_items_default_ordering_on_created(
    user_api_client, user, feed_item, user_feed_subscription
):
    feed_item_2 = baker.make(FeedItem, feed__name="dummy")
    baker.make(UserFeedSubscription, user=user, feeds=[feed_item_2.feed])

    response = user_api_client.get(
        "/feed/feed-item/?format=json", format="json"
    )
    data = response.json()

    assert response.status_code == 200
    assert data["count"] == 2
    assert data["results"][0]["id"] == feed_item_2.id
    assert data["results"][1]["id"] == feed_item.id


def test_feed_unsubscribe_for_user(
    user_api_client, feed, user_feed_subscription
):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/unsubscribe/?format=json", data={}, format="json"
    )

    assert response.status_code == 200
    assert response.json() == {"status": f"feed:{feed.name} unsubscribed"}


def test_feed_unsubscribe_for_user_without_sub(user_api_client, feed):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/unsubscribe/?format=json", data={}, format="json"
    )

    assert response.status_code == 400
    assert response.json() == {"status": f"feed: {feed.name} is not subscribed"}


def test_feed_subscribe_for_user(user_api_client, feed):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/subscribe/?format=json", data={}, format="json"
    )

    assert response.status_code == 200
    assert response.json() == {"status": f"feed: {feed.name} subscribed"}


def test_feed_subscribe_for_user_already_sub(
    user_api_client, feed, user_feed_subscription
):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/subscribe/?format=json", data={}, format="json"
    )

    assert response.status_code == 400
    assert response.json() == {
        "status": f"feed: {feed.name} already subscribed"
    }


def test_feed_force_update_without_sub(user_api_client, feed):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/force-update/?format=json", format="json"
    )
    assert response.status_code == 400
    assert response.json() == {"status": f"feed:{feed.name} is not subscribed"}


def test_read_item_status(
    user_api_client, feed, feed_item, user_feed_subscription
):
    name = "test title"
    feed_item_2 = baker.make(FeedItem, title=name, feed=feed)
    response = user_api_client.get(
        f"/feed/feed-item/{feed_item.id}/?format=json", format="json"
    )

    assert response.status_code == 200
    response = user_api_client.get(
        "/feed/feed-item/?format=json", format="json"
    )
    data = response.json()
    assert data["count"] == 2
    assert data["results"][0]["id"] == feed_item_2.id
    assert not data["results"][0]["has_read"]
    assert data["results"][1]["id"] == feed_item.id
    assert data["results"][1]["has_read"]


@pytest.mark.django_db
@patch("feed.feed_parser.Parser._fetch_data", return_value=ALGEMEEN)
def test_feed_force_update(
    mock_api, user_api_client, feed, user_feed_subscription
):
    response = user_api_client.post(
        f"/feed/feed/{feed.id}/force-update/?format=json", format="json"
    )

    assert response.status_code == 200
    assert response.json() == {
        "status": f"fetched feed:{feed.name} successfully"
    }
    assert FeedItem.objects.filter(title="Zeker").count() == 1
