from bs4 import BeautifulSoup
from os import path, listdir, system
from requests import get

from init import version


def update(repo="gregor-dietrich/bns-upk-manager", current_version=version):
    print("Checking for updates...")
    try:
        response = get("https://github.com/" + repo + "/releases/latest")
        doc = BeautifulSoup(response.text, "html.parser")
        current_version = "".join(current_version.split("."))
        latest_version = "".join(doc.select_one("div.label-latest div ul li a")["title"].split("v")[1].split("."))
        file_url = "https://github.com" + doc.select_one("details div.Box div div.Box-body a")["href"]
        file_name = file_url.split("/")[-1]
        if float(latest_version) > float(current_version):
            decision = ""
            while decision not in ["y", "n"]:
                decision = input("New version found! Download now (y/n)? ")
                if decision == "y":
                    break
                elif decision == "n":
                    return
            if not path.exists("./" + file_name):
                file_binary = get(file_url)
                with open("./" + file_name, "wb") as file:
                    file.write(file_binary.content)
            if file_name.endswith(".zip"):
                from zipfile import ZipFile
            elif file_name.endswith(".7z"):
                from py7zr import SevenZipFile as ZipFile
            else:
                print("Invalid archive format!")
                return
            with ZipFile("./" + file_name, "r") as archive:
                archive.extractall("./download")
            with open("./update.bat", "w") as batch:
                batch.write("@echo off\n")
                patch_files = listdir("./download")
                for patch_file in patch_files:
                    if patch_file.endswith(".exe"):
                        batch.write("taskkill /f /im " + patch_file + "\n")
                batch.write("@ping -n 3 localhost> nul\n" +
                            "robocopy download\\ .\\ *.* /move /s /is /it\n" +
                            "rmdir /s /q download\n" +
                            "del " + file_name + "\n" +
                            "del update.bat\n" +
                            "tk_upk_manager.exe")
            system('cmd /c "update.bat"')
            exit()
        else:
            print("Already up to date!")
    except ConnectionError:
        print("Connection failed! Is your internet connection working?")
        return
    except (TypeError, ValueError, IndexError):
        print("Something went wrong! Please try again later.")
