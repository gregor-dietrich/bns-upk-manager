from hashlib import sha1
from os import path
from winreg import ConnectRegistry, EnumValue, HKEY_CURRENT_USER, HKEY_LOCAL_MACHINE, OpenKey


def checksum(file_name):
    hash_obj = sha1()
    with open(file_name, "rb") as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    return hash_obj.hexdigest()


def search_reg(scope):
    if scope == "HKCU":
        a_reg = ConnectRegistry(None, HKEY_CURRENT_USER)
        a_key = "Software\\Classes\\Local Settings\\Software\\Microsoft\\Windows\\Shell\\MuiCache\\"
    elif scope == "HKLM":
        a_reg = ConnectRegistry(None, HKEY_LOCAL_MACHINE)
        a_key = "SOFTWARE\\WOW6432Node\\NCWest\\BnS\\"
    else:
        return
    count = 0
    try:
        key = OpenKey(a_reg, a_key)
        while True:
            name, value, value_type = EnumValue(key, count)
            if scope == "HKCU":
                if value == "Blade & Soul by bloodlust(x86)":
                    game_path = name.split(".")[0].split("\\")
                    game_path.pop()
                    game_path.pop()
                    print("Game path found in HKCU!")
                    return "/".join(game_path) + "/"
            elif scope == "HKLM":
                if name == "BaseDir":
                    print("Game path found in HKLM!")
                    return value
            count += 1
    except (WindowsError, OSError, FileNotFoundError):
        pass


def find_game_path(default):
    # Try default install dir
    if path.exists(default):
        return default
    # Search HKCU
    result = search_reg("HKCU")
    # Search HKLM
    if result is None:
        result = search_reg("HKLM")
    # Fix Backslashes
    try:
        if "\\" in result:
            result = result.split("\\")
            result = "/".join(result)
        if path.exists(result):
            return result
    except TypeError:
        pass
