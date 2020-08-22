import json


def main():
    secrets = {}
    secrets['client_id'] = input("New Client ID: ")
    secrets['api_key'] = input("New API key: ")
    secrets['api_key_secret'] = input("New API key secret: ")
    choice = None
    options = ["y", "n"]
    while choice not in options:
        choice = input("Save these settings? (y/n) ")
    if choice == "y":
        with open("secrets.json", "w") as secrets_file:
            json.dump(secrets, secrets_file, indent=4)


if __name__ == "__main__":
    main()
