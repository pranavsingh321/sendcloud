from rest_framework import serializers

from feed.models import Feed, FeedItem, UserFeedItem


class FeedSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feed
        fields = (
            "id",
            "url",
            "name",
        )


class FeedItemSerializer(serializers.ModelSerializer):
    has_read = serializers.SerializerMethodField()

    def get_has_read(self, obj):
        return UserFeedItem.objects.filter(
            user=self.context.get("request").user, feed_item=obj
        ).exists()

    class Meta:
        model = FeedItem
        fields = ("id", "feed", "title", "description", "has_read")


class UserFeedItemSerializer(serializers.ModelSerializer):
    feed_item = FeedItemSerializer()

    class Meta:
        model = UserFeedItem
        fields = (
            "id",
            "user",
            "feed_item",
        )
