# Discord Updater
Discord auto-updater program for APT-based Linux distros.

# Features
- Automatically fetch and install a new `discord` package if needed.
- Optionally, install [Vencord](https://vencord.dev).

# Requirements
This project requires the following packages:
- `debian`, `requests`

Install with `pip install debian requests`

# Running the script
To install a new version of the `discord` package:

`sudo python3 main.py`

To install Vencord:

`python3 main.py -vencord -skipdiscord`

Optional flags:
- `-y`: Do not ask for confirmation.
- `-nocleanup`: Do not clean up installed `.deb` packages.
- `-ignoreversion`: Ignore same versions of the `discord` package and install anyways.

# The developer of this project is not responsible for any damages caused by use or misuse of this script.
