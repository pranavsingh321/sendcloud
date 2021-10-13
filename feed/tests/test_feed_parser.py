from unittest.mock import patch

import pytest
from requests.exceptions import ConnectionError, Timeout
from rest_framework.exceptions import APIException

from feed.feed_parser import fetch_feed
from feed.tests.data_dump import ALGEMEEN, FEEDBURNER


@pytest.mark.parametrize(
    ("exception", "message"),
    (
        (
            ConnectionError,
            "Failed to fetch: http://dummy.com  due to connection error",
        ),
        (Timeout, "Failed to fetch: http://dummy.com  due to timeout error"),
    ),
)
@patch("feed.feed_parser.Parser._ext_get_api_call")
def test_external_exception(mock_api_call, exception, message):
    mock_api_call.side_effect = exception
    with pytest.raises(APIException) as exinfo:
        [item for item in fetch_feed(url="http://dummy.com")]
    assert str(exinfo.value) == message


@pytest.mark.parametrize(
    ("url", "api_return", "data"),
    (
        ("http://www.nu.nl/rss/Algemeen", ALGEMEEN, ("Zeker", "Een man")),
        (
            "https://feeds.feedburner.com/tweakers/mixed",
            FEEDBURNER,
            ("Asustor", "Asustor heeft"),
        ),
    ),
)
@patch("feed.feed_parser.Parser._fetch_data")
def test_parse_xml_data(mock_api_call, url, api_return, data):
    mock_api_call.return_value = api_return
    assert [data] == [
        (item.title, item.description) for item in fetch_feed(url)
    ]
