import logging
from dataclasses import dataclass
from typing import Iterable, Optional

import requests
from bs4 import BeautifulSoup
from rest_framework.exceptions import APIException

logger = logging.getLogger(__name__)


@dataclass
class Item:
    title: str
    description: str


class Parser:
    def __init__(self, url: str):
        self.url = url
        self.field_name = "item"

    def parse(
        self,
    ) -> Iterable[Item]:
        raise NotImplementedError

    def _ext_get_api_call(
        self,
    ):
        return requests.get(url=self.url)

    def _fetch_data(
        self,
    ) -> Optional[bytes]:
        try:
            res = self._ext_get_api_call()
        except requests.exceptions.ConnectionError:
            err_msg = f"Failed to fetch: {self.url}  due to connection error"
            logger.error(err_msg)
            raise APIException(err_msg)
        except requests.exceptions.Timeout:
            err_msg = f"Failed to fetch: {self.url}  due to timeout error"
            logger.error(err_msg)
            raise APIException(err_msg)

            if res.status_code != 200:
                raise APIException(f"Failed to fetch data: {res.text}")

        return res.content


class XMLParser(Parser):
    def __init__(self, url: str):
        super().__init__(url)
        self.data_type = "xml"

    def parse(
        self,
    ):
        for item in BeautifulSoup(
            self._fetch_data(), features=self.data_type
        ).find_all(self.field_name):
            yield Item(item.title.text, item.description.text)


def fetch_feed(url: str) -> Iterable[Item]:
    """
    Get the feed data
    """
    parser = XMLParser(url=url)
    return parser.parse()
