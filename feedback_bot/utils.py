import random
import string

import yaml


def generate_random_string(length: int = 12) -> str:
    return "".join(random.choices(string.ascii_letters + string.digits, k=length))


def parse_messages(file_path: str) -> dict[str, str]:
    messages = {}
    with open(file_path, "r") as file:
        for key, msg in yaml.safe_load(file).items():
            if isinstance(msg, list):
                for index, line in enumerate(msg):
                    msg[index] = str(line)
                messages[key] = "\n".join(msg)
            else:
                messages[key] = str(msg)
    return messages
