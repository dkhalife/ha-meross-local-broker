from hashlib import md5
from uuid import uuid4
from logger import get_logger
import argparse
from constants import DEFAULT_USER_ID
from database import init_db
from db_helper import dbhelper
from model.db_models import User
from model.enums import EventType

l = get_logger("setup")

def setup_account(email: str, password: str) -> User:
    user_key = str(md5(uuid4().bytes).hexdigest().lower())
    user_id = DEFAULT_USER_ID

    # The new version of Meross API uses a hashed password as clear password (md5)
    #  We do the same to maintain compatibility with low-level MerossIot API
    hashed_pass = md5(password.encode("utf8")).hexdigest()
    user = dbhelper.add_update_user(user_id=user_id, email=email, password=hashed_pass, user_key=user_key)
    dbhelper.add_update_configuration(local_user_id=user.user_id)
    l.info(f"User: %s, mqtt_key: %s", user.email, user.mqtt_key)
    dbhelper.store_event(event_type=EventType.CONFIGURATION_CHANGE, details=f"Login username/password has been changed.")
    return user

def main():
    init_db()

if __name__ == '__main__':
    main()
