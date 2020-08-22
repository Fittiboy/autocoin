import json


def main():
    fiat = input("New fiat (should be three uppercase letters, like EUR): ")
    choice = None
    options = ["y", "n"]
    while choice not in options:
        choice = input(f"Set new fiat to {fiat.upper()}? (y/n) ")
    if choice == "y":
        with open("fiat.json", "w") as fiat_file:
            json.dump(fiat, fiat_file)


if __name__ == "__main__":
    main()
