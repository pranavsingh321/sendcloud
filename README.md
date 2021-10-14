# RSS Feed Example

This is an RSS feed manager example.

## Requirements
* Follow multiple feeds
* Unfollow feed
* List feed items belonging to one feed as per user subscription
* Mark feed item as read upon detail fetch
* Filter feed items per feed or across feeds
* Sort feed items based on update/create.
* Force feed update
* Feeds updated in background task at regular intervals with back-off mechanism
* Notify users/subscribers in case of background task failure to fetch the feed
* Test case to simulate failure

## Services
* django based sendcloud api
* mariadb
* redis
* celery
* celery-beat

## Installation
   The setup mounts current directory in container to allow real-time changes.
### Host
  pip3 install poetry

  poetry install

  poetry shell

  pre-commit install

  cp .env.example .env

### Services setup
  docker-compose up

### Requirements
* Python 3.7 and pip
* docker-compose

## Usage
   DRF based api can be accessed at http://0.0.0.0:8001/feed/. All the endpoints require login which can be done easily in DRF browsable api.

   There are 5 endpoints:
* /feed/feed/
* /feed/feed-item/
* /feed/feed/{id}/subscribe/
* /feed/feed/{id}/unsubscribe/
* /feed/feed/{id}/force-update/

  There is support of filtering feed-items based on feed name e.g. "/feed/feed-item/?feed=dummy&format=json" and feed items are sorted based on creation date.

  Fetching of feed items is done through celery task and mail will be sent in case of failure.

  Feed item is considered as read if it detail view is called on that feed item.

## Test
   pytest

## Miscellaneous
Bootstrap/initial data can be loaded with following command inside the sendcloud:

python manage.py loaddata < db.json


## Improvements
* Refactor settings module
* Running services without root user
