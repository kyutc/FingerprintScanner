import json
import jsonmerge
import os


def load() -> dict:
    with open("config.json" if os.path.exists("config.json") else "config.default.json", "r") as config_file, \
            open("config.default.json", "r") as default_config_file:
        default_config = json.load(default_config_file)
        config = json.load(config_file)
        config = jsonmerge.merge(default_config, config)
        return config


def save(config: dict) -> bool:
    with open("config.json.tmp", "w") as config_file:
        try:
            json.dump(config, config_file, indent=4)
        except:
            os.remove("config.json.tmp")
            return False
    os.replace("config.json.tmp", "config.json")  # json.dump will garble files on error
    return True


if __name__ == '__main__':
    config = load()
    save(config)
