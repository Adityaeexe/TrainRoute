from typing import Dict


class Train:
    def __init__(self, name: str, train_id: int, capacity: int):
        self.name = name
        self.train_id = train_id
        self.capacity = capacity
        self.availability: Dict[str, int] = {}

def get_berth_availability(trains: Dict[int, Train], train_id: int, date: str) -> int:
    train = trains.get(train_id)
    return train.availability.get(date, 0) if train else 0