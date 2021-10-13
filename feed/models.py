from django.contrib.auth.models import User
from django.db import models
from django_enumfield import enum


class SourceType(enum.Enum):
    HTML = 1
    XML = 1


class Feed(models.Model):
    """
    Feed specific data
    """

    url = models.URLField()
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class FeedItem(models.Model):
    """
    Feed items specific data
    """

    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class UserFeedSubscription(models.Model):
    """
    Holds user feed subscriptions data
    """

    user = models.OneToOneField(
        User,
        primary_key=True,
        related_name="subscription",
        on_delete=models.CASCADE,
    )
    feeds = models.ManyToManyField(
        Feed,
        related_name="subscribers",
        blank=True,
    )

    def __str__(self):
        return f"user: {self.user} subscriptions"


class UserFeedItem(models.Model):
    """
    Holds feed items read by user
    """

    user = models.ForeignKey(
        User, related_name="read_users", on_delete=models.CASCADE
    )
    feed_item = models.ForeignKey(
        FeedItem, related_name="read_items", on_delete=models.CASCADE
    )

    def __str__(self):
        return f"user: {self.user}, read items: {self.feed_item.title}"
