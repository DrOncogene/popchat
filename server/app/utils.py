"""
chat utility helper functions
"""
from passlib.context import CryptContext

from app.schemas.models import MessageSchema, DayMessages


HASHER = CryptContext(schemes=["bcrypt"], deprecated="auto")


def group_messages(messages: list[MessageSchema]) -> list[dict]:
    """
    takes a list of messages and groups them by date
    """

    new_messages: list[DayMessages] = []
    for message in messages:
        when = message.when
        when_date = when.date().strftime("%Y-%m-%d")
        for day in new_messages:
            day_date = day.date
            day_messages = day.messages
            if day_date == when_date:
                day_messages.append(message)
                break
        else:
            new_messages.append(
                DayMessages(
                    date=when_date,
                    messages=[MessageSchema(**(message.model_dump()))],
                )
            )

    return [msg.model_dump() for msg in new_messages]


def create_passwd_hash(passwd: str) -> str:
    """
    returns the hash of the password
    """
    return HASHER.hash(passwd)


def verify_passwd(passwd: str, passwd_hash: str) -> bool:
    """
    verifies the password
    """
    return HASHER.verify(passwd, passwd_hash)
