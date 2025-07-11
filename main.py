from requests import get, HTTPError
from subprocess import Popen, PIPE
from sys import argv, exit as sysexit
from os import getuid, remove, setuid, getenv, setgid, environ
from os.path import join, exists, dirname, basename
from time import sleep
from json import load
from debian.debfile import DebFile

def run(command: str, use_pipe: bool=True) -> tuple[str, str, int] | bool:
    process = Popen(
        command,
        shell=True,
        stdout=PIPE if use_pipe else None,
        stderr=PIPE if use_pipe else None
    )
    if use_pipe:
        stdout, stderr = process.communicate()
        return stdout.decode().strip(), stderr.decode().strip(), process.returncode
    else:
        code = process.wait()
        return code == 0

def get_discord_version():
    path_to_discord = "/usr/share/discord"

    if exists(path_to_discord):
        build_file = join(path_to_discord, "resources", "build_info.json")

        with open(build_file, "r") as f:
            version_info = load(f)

        return version_info["version"]
    
    return None

def get_deb_version(fp: str):
    deb = DebFile(fp)
    return deb.debcontrol().get("Version")

def check_input(prompt: str) -> None:
    confirm = input(prompt)
    
    match confirm.lower():
        case "n":
            print("exit")
            sysexit(0)
        case "y":
            print("Proceeding...")
            sleep(1.5)
        case _:
            print("defaultexit")
            sysexit(0)

def write_file(path: str, r_content) -> bool:
    try:
        with open(path, "wb") as f:
            f.write(r_content)
    except OSError as e:
        print(f"An error occured while writing content to file\n{e}")
        return False
    
    return True

def get_file(url: str, filepath: str) -> str | bool:
    headers = {
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36"
    }

    try:
        r = get(url, headers=headers)
    except HTTPError as e:
        print(f"An HTTP error occured while sending a request to '{url}'")
        return False
    
    if r.status_code == 200:
        success = write_file(filepath, r.content)

        if not success:
            return False
        
    else:
        print(f"A non-200 response code recieved from '{url}'.")
        return False
    
    return filepath if exists(filepath) else False

def install_package(file: str) -> bool:
    if not file.endswith(".deb"):
        print(f"File {file}\nis not a .deb file!")
        sysexit(0)

    COMMAND = f"sudo dpkg -i {file}"

    print(f"Running '{COMMAND}'")
    check_input("Continue? (y/N): ")
    stdout, stderr, code = run(COMMAND)

    if code == 0:
        print(f"Successfully installed {basename(file)}")
        return True
    else:
        print(f"An error occured while installing {file}\nErr: {stderr}")
        sysexit(0)

def cleanup(deb_fp: str) -> None:
    if exists(deb_fp):
        print(f"Cleaning up '{deb_fp}'")
        try:
            remove(deb_fp)
        except OSError as e:
            print(f"An error occured while cleaning up.\nErr: {e}")

def install_vencord(ask: bool) -> bool:
    check_root(reason="vencord")
    
    COMMAND = f'sh -c "$(curl -sS https://raw.githubusercontent.com/Vendicated/VencordInstaller/main/install.sh)"'

    print(f"Running '{COMMAND}'")
    if not ask:
        check_input("Continue? (y/N): ")

    success = run(COMMAND, False)

    if success == True:
        print("Successfully exited Vencord installer.")
        return True
    else:
        print(f"An error occured while installing vencord.")
        return False

def check_root(reason="pkgs"):
    uid = getuid()

    match reason:
        case "pkgs":

            if uid != 0:
                print("This script requires root priviliges to install packages.")
                sysexit(0)
        case "vencord":
                
            if uid == 0:
                print("Run the script without root and with the -skipdiscord and -vencord flags")
                sysexit(0)

def check_version(discord: str, deb: str, ignore_flag: bool) -> bool:
    if discord is not None and\
        not ignore_flag and\
        discord == deb:
            print(f"discord system package is already at the newest version ({discord})")
            return True
    
    return False

def main(argv):
    PATH = dirname(__file__)
    URL = "https://discord.com/api/download?platform=linux"
    DEB_FILE_PATH = join(PATH, "discord.deb")
    NO_ASK = "-y" in argv
    NO_CLEANUP = "-nocleanup" in argv
    INSTALL_VENCORD = "-vencord" in argv
    SKIP_DISCORD = "-skipdiscord" in argv
    IGNORE_VERSION = "-ignoreversion" in argv
    is_latest_version = False

    DISCORD_VERSION = get_discord_version()

    if not INSTALL_VENCORD or not SKIP_DISCORD:
        check_root()

    if not SKIP_DISCORD:
        if not exists(DEB_FILE_PATH):
            print(f"Will download file at '{URL}'")
            
            if not NO_ASK:
                check_input("Continue? (y/N): ")
            
            print("Downloading discord package...")
            deb_path = get_file(URL, DEB_FILE_PATH)

            if not deb_path:
                sysexit(1)

            print("Successfully downloaded package.")
        else:
            deb_path = DEB_FILE_PATH
        DEB_VERSION = get_deb_version(deb_path)
        sleep(0.5)

        is_latest_version = check_version(DISCORD_VERSION, DEB_VERSION, IGNORE_VERSION)

        if not is_latest_version:
            print(f"Found Debian package at {deb_path}.")
            if not NO_ASK:
                check_input("Install it? (y/N): ")

            install_package(deb_path)

    if INSTALL_VENCORD:
        install_vencord(NO_ASK)

    if not NO_CLEANUP:
        cleanup(DEB_FILE_PATH)

    print("done")

if __name__ == "__main__":
    main(argv)
