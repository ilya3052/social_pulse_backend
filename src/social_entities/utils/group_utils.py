from enum import IntEnum, Enum


async def get_item_stats(msg):
    reactions_count, repost_count, replies_count = 0, 0, 0
    views_count = msg.views if msg.views else 0
    if reactions := msg.reactions:
        for result in reactions.results:
            reactions_count += result.count

    repost_count += msg.forwards if msg.forwards else 0

    if replies := msg.replies:
        replies_count += replies.replies if replies.replies else 0
    return views_count, reactions_count, replies_count, repost_count


class Status(IntEnum):
    Accepted = 0
    Unaccepted = 1
    ContactsNotFound = 2
    Error = 3


class Platforms(Enum):
    VK = 'VK'
    TG = 'TG'
