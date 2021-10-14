import logging

from celery import Task, shared_task
from django.contrib.auth.models import User
from rest_framework.exceptions import APIException

from feed.email import send_feed_failure_email
from feed.feed_parser import fetch_feed
from feed.models import Feed, FeedItem

logger = logging.getLogger(__name__)


@shared_task()
def send_mail_user(user_id, feed_name):
    user = User.objects.get(pk=user_id)
    logger.info(f" Sending email to user, id: {user_id}, feed: {feed_name}")
    send_feed_failure_email(
        user_email=user.email,
        message=f"failed to fetch feed:{feed_name}",
        subject="Feed failure",
    )


class BaseTaskRetry(Task):
    autoretry_for = (APIException,)
    retry_kwargs = {"max_retries": 5}
    retry_backoff = True
    retry_jitter = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        try:
            feed = Feed.objects.get(pk=args[0])
        except Feed.DoesNotExist:
            return

        logger.info(f" Failed to fetch feed: {args[0]}")

        for subscriber in feed.subscribers.all():
            send_mail_user.apply(args=(subscriber.user.id, feed.name))

        return super().on_failure(exc, task_id, args, kwargs, einfo)


@shared_task(base=BaseTaskRetry)
def fetch_feed_sub_task(feed_id):
    items = None
    try:
        feed = Feed.objects.get(pk=feed_id)
    except Feed.DoesNotExist:
        logger.warning(f"Feed, id: {feed.id} not found")
        return

    logger.info(f"Fetching items for feed, id: {feed.id}, name: {feed.name}")

    items = fetch_feed(feed.url)

    for item in items:
        FeedItem.objects.get_or_create(
            feed=feed, title=item.title, description=item.description
        )

    logger.info(
        f"Successfully fetched items for feed, id: {feed.id}, name: {feed.name}"
    )


@shared_task()
def fetch_feeds_task():
    """
    Task to fetch feed items on regular intervals specified in celery beat periodic task
    """

    for feed in Feed.objects.all():
        fetch_feed_sub_task.apply_async(args=(feed.id,))
