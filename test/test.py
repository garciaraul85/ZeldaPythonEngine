from typing import Any, Dict, TypeVar

T = TypeVar("T")


class User:

    def __init__(self, name: str, village: str, value: int) -> None:
        self.value = value
        self.name = name
        self.village = village


def user_from_dict(s: Dict[str, Any]) -> User:
    return User(**s)


def user_to_dict(x: User) -> Dict[str, Any]:
    return vars(x)


data = {"name": "Uzumaki Naruto", "village": "Leaf Village", "value": 30}
usr = user_from_dict(data)
print(usr.name)
print(usr.value)
usr_dict = user_to_dict(usr)
print(usr_dict["village"])
