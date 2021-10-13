import logging

from django.shortcuts import get_object_or_404
from rest_framework import filters, status, viewsets
from rest_framework.authentication import (
    SessionAuthentication,
    TokenAuthentication,
)
from rest_framework.decorators import (
    api_view,
    authentication_classes,
    permission_classes,
)
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from feed.feed_parser import fetch_feed
from feed.models import Feed, FeedItem, UserFeedItem, UserFeedSubscription
from feed.serializers import (
    FeedItemSerializer,
    FeedSerializer,
    UserFeedItemSerializer,
)

logger = logging.getLogger(__name__)


class FeedView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = FeedSerializer
    permission_classes = (IsAuthenticated,)
    ordering = (("-id"),)
    filter_backends = (filters.OrderingFilter,)

    def get_queryset(
        self,
    ):
        return Feed.objects.all()


class FeedItemView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = FeedItemSerializer
    permission_classes = (IsAuthenticated,)
    ordering_fields = (("title"),)
    ordering = (("-created"),)
    filter_backends = (filters.OrderingFilter,)

    def get_queryset(
        self,
    ):
        queryset = FeedItem.objects.filter(
            feed__subscribers__user=self.request.user
        )
        feed_name = self.request.query_params.get("feed")
        if feed_name:
            return queryset.filter(feed__name=feed_name)
        return queryset

    def retrieve(self, request, *args, **kwargs):
        """
        Override to create UserFeedItem to mark read items
        """
        UserFeedItem.objects.get_or_create(
            user=self.request.user, feed_item=self.get_object()
        )
        return super().retrieve(request, *args, **kwargs)


class UserFeedItemView(viewsets.ReadOnlyModelViewSet):
    authentication_classes = (TokenAuthentication, SessionAuthentication)
    serializer_class = UserFeedItemSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(
        self,
    ):
        return UserFeedItem.objects.filter(user=self.request.user)


@api_view(["POST"])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def subscribe(request, feed_pk):
    feed = get_object_or_404(Feed, pk=feed_pk)

    feed_sub, created = UserFeedSubscription.objects.get_or_create(
        user=request.user
    )
    if not created:
        return Response(
            {"status": f"feed: {feed.name} already subscribed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    feed_sub.feeds.add(feed)
    return Response(
        {"status": f"feed: {feed.name} subscribed"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def unsubscribe(request, feed_pk):
    feed = get_object_or_404(Feed, pk=feed_pk)

    if (
        not hasattr(request.user, "subscription")
        or feed not in request.user.subscription.feeds.all()
    ):
        return Response(
            {"status": f"feed: {feed.name} is not subscribed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    request.user.subscription.feeds.remove(feed)
    return Response(
        {"status": f"feed:{feed.name} unsubscribed"},
        status=status.HTTP_200_OK,
    )


@api_view(["POST"])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((IsAuthenticated,))
def force_update(request, feed_pk):
    feed = get_object_or_404(Feed, pk=feed_pk)
    items = None

    # check if usesr is subscribed to the feed
    if (
        not hasattr(feed, "subscribers")
        or not feed.subscribers.filter(user=request.user).exists()
    ):
        return Response(
            {"status": f"feed:{feed.name} is not subscribed"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    try:
        items = fetch_feed(feed.url)
    except APIException as ae:
        logger.error(
            f"Failed to force fetch items for feed url: {feed.url} due to exception: {ae}"
        )
        return Response(
            {"status": f"falied to fetch feed:{feed.name}"},
            status=status.HTTP_424_FAILED_DEPENDENCY,
        )

    for item in items:
        FeedItem.objects.get_or_create(
            feed=feed, title=item.title, description=item.description
        )

    return Response(
        {"status": f"fetched feed:{feed.name} successfully"},
        status=status.HTTP_200_OK,
    )
