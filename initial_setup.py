import setadd
import setfiat
import setsecrets


def main():
    print()
    setadd.main()
    print()
    setfiat.main()
    print()
    setsecrets.main()
    print("\nTo change your address later, run `python setadd.py` in " +
          "this directory! You can usually paste your address here with " +
          "Ctrl+Shift+V or a right-click.")
    print("\nShould you want to change the fiat currency for whatever " +
          "reason, you can run `python setfiat.py` the same way as " +
          "described above for `setadd.py`.")
    print("\nAs you might have guessed, you can also run `python " +
          "setsecrets.py` for your Client ID, API key and API key secret.")


if __name__ == "__main__":
    main()
