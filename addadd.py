import json
import sys


def main():
    newadds = sys.argv[1:]
    try:
        with open("addresses.json") as add_file:
            addlist = json.load(add_file)
    except IOError:
        addlist = []
    addlist += newadds
    with open("addresses.json", "w") as add_file:
        json.dump(addlist, add_file, indent=4)


if __name__ == "__main__":
    main()
