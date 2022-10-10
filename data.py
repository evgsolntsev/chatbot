"""Chat data import/export."""

import json

from markov import Chain

class Data:
    """This class represents all data for one dialog."""

    chain = None
    dungeon_subscribers = None
    tmp_dungeon_subscribers = None

    def __init__(
            self, data,
            probability=10, dungeon_subscribers=None, tmp_dungeon_subscribers=None):

        self.chain = Chain(data, probability=probability)

        if dungeon_subscribers is None:
            dungeon_subscribers = []
        self.dungeon_subscribers = dungeon_subscribers

        if tmp_dungeon_subscribers is None:
            tmp_dungeon_subscribers = []
        self.tmp_dungeon_subscribers = tmp_dungeon_subscribers

    def write_to_file(self, int_id):
        """Writes Data to file."""

        data = json.dumps({
            "data": self.chain.data,
            "probability": self.chain.probability,
            "dsubscribers": self.dungeon_subscribers,
            "dtmpsubscribers": self.tmp_dungeon_subscribers
        })
        with open(to_filename(int_id), "w+", encoding="utf-8") as destination:
            destination.write(data)

    def add_dungeon_subscriber(self, subscriber):
        """Adds subscriber."""

        if subscriber not in self.dungeon_subscribers:
            self.dungeon_subscribers.append(subscriber)

    def remove_dungeon_subscriber(self, subscriber):
        """Removes subscriber."""

        new_subscribers = []
        for sub in self.dungeon_subscribers:
            if sub != subscriber:
                new_subscribers.append(sub)
        self.dungeon_subscribers = new_subscribers

    def add_tmp_dungeon_subscriber(self, subscriber):
        """Adds subscriber."""

        if subscriber not in self.tmp_dungeon_subscribers:
            self.tmp_dungeon_subscribers.append(subscriber)

def read_from_file(int_id):
    """Reads Data from a file."""

    try:
        with open(to_filename(int_id), "r", encoding="utf-8") as source:
            dump = json.loads(source.read())
            return Data(
                dump["data"], probability=dump["probability"],
                dungeon_subscribers=dump.get("dsubscribers", []),
                tmp_dungeon_subscribers=dump.get("dtmpsubscribers", []))
    except OSError:
        return Data({})

def to_filename(int_id):
    """Converts integer ID to filename."""

    return "data/" + str(int_id) + ".json"
