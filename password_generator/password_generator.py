import random
import string

rng = random.SystemRandom()

def ask_yes_no(question):

    while True:
        answer = input(question + " (y/n): ").strip().lower()
        if answer in ("y", "yes"):
            return True
        if answer in ("n", "no"):
            return False
        print("Please type y or n.")


def ask_number(question, minimum=1, maximum=100):

    while True:
        value = input(question).strip()
        if not value.isdigit():
            print("Please enter a number.")
            continue
        value = int(value)
        if value < minimum or value > maximum:
            print(f"Enter a number between {minimum} and {maximum}.")
            continue
        return value


def build_password(length, use_letters, use_numbers, use_symbols):

    groups = []
    if use_letters:
        groups.append(string.ascii_letters)
    if use_numbers:
        groups.append(string.digits)
    if use_symbols:
        groups.append("!@#$%^&*()-_=+[]{};:,.?")


    password_chars = [rng.choice(group) for group in groups]


    all_chars = "".join(groups)
    for _ in range(length - len(password_chars)):
        password_chars.append(rng.choice(all_chars))

    rng.shuffle(password_chars)
    return "".join(password_chars)


def main():
    print("=" * 36)
    print("       PASSWORD GENERATOR")
    print("=" * 36)

    while True:
        length = ask_number("Enter password length (4-64): ", 4, 64)

        use_letters = ask_yes_no("Include letters?")
        use_numbers = ask_yes_no("Include numbers?")
        use_symbols = ask_yes_no("Include symbols?")

        if not (use_letters or use_numbers or use_symbols):
            print("You must select at least one option. Try again.\n")
            continue

        count = ask_number("How many passwords do you want? ", 1, 20)

        print("\nYour generated password(s):")
        for i in range(1, count + 1):
            pwd = build_password(length, use_letters, use_numbers, use_symbols)
            print(f"  {i}. {pwd}")

        print()
        if not ask_yes_no("Generate more passwords?"):
            print("Thanks for using the Password Generator. Stay safe!")
            break
        print()


if __name__ == "__main__":
    main()