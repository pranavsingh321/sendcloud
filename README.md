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

### Host installation
  pip3 install poetry

  poetry install

### Services setup
  docker-compose up

### Requirements
* Python 3.7 and pip
* docker-compose

## Usage
  poetry shell

  pre-commit install

## Test
   pytest

Bootstrap/initial data can be loaded with following command inside the sendcloud:

python manage.py loaddata < db.json


## Improvements
* Refactor settings module
* Running services without root user
