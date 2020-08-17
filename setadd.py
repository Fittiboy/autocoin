import json

if __name__ == "__main__":
    address = input("New address: ")
    choice = None
    options = ["y", "n"]
    while choice not in options:
        choice = input(f"Set new address to {address}? (y/n) ")
    if choice == "y":
        with open("address.json", "w") as address_file:
            json.dump(address, address_file)
