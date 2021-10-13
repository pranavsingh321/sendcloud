from sendcloud.settings import *  # noqa

TEST = True
DEBUG = True
DATABASE_URL = env.str("TEST_DATABASE_URL")  # noqa
