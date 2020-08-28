import json
from hashlib import sha1
from os import path, remove


def checksum(file_name):
    hash_obj = sha1()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def settings_load(settings_location, default_values, charset):
    if not path.exists(settings_location):
        print("File %s not found!" % settings_location)
        return default_values
    # Load settings.json as dictionary
    print("Loading settings from %s..." % settings_location)
    with open(settings_location, "r", encoding=charset) as file:
        values = file.read()
    try:
        settings_values = json.loads(values)
        for k in default_values.keys():
            if k not in settings_values.keys():
                settings_values[k] = default_values[k]
        print("Successfully loaded profile '%s'!" % settings_location)
        return settings_values
    except json.JSONDecodeError:
        print("ERROR: Invalid JSON syntax detected!")
        if input("Delete %s and overwrite with default (y/n)? " % ("./profiles/" + settings_location)) == "y":
            remove(settings_location)
            with open(settings_location, "w", encoding=charset) as settings_file:
                json.dump(default_values, settings_file, sort_keys=True, indent=4)
        else:
            print("Aborting profile import...")
            return default_values
