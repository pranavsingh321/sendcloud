from django.conf.urls import include, url
from django.urls import path
from rest_framework.routers import DefaultRouter

from feed import views

router = DefaultRouter()
router.register(r"feed", views.FeedView, "Feed")
router.register(r"feed-item", views.FeedItemView, "FeedItem")
router.register(r"user-feed-item", views.UserFeedItemView, "UserFeedItem")


urlpatterns = [
    url(
        r"^feed/(?P<feed_pk>[0-9]+)/subscribe/$",
        views.subscribe,
        name="feed-subscribe",
    ),
    url(
        r"^feed/(?P<feed_pk>[0-9]+)/unsubscribe/$",
        views.unsubscribe,
        name="feed-unsubscribe",
    ),
    url(
        r"^feed/(?P<feed_pk>[0-9]+)/force-update/$",
        views.force_update,
        name="feed-force-udpate",
    ),
    path("", include(router.urls)),
]
