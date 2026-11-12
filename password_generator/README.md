# Password Generator

**Auspify Internship | Task 1 (Easy)**

A command-line Python application that generates secure, customizable random passwords.

## What it does

- Takes the password length from the user
- Lets the user choose whether to include letters, numbers and symbols
- Generates one or more random passwords at once
- Guarantees at least one character from each selected type
- Lets the user keep generating passwords until they choose to quit

## Skills used

- Python basics (functions, loops, input validation)
- `random` module
- String manipulation

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Run:

```bash
python password_generator.py
```

No extra libraries are needed.

## Sample output

```
====================================
       PASSWORD GENERATOR
====================================
Enter password length (4-64): 12
Include letters? (y/n): y
Include numbers? (y/n): y
Include symbols? (y/n): y
How many passwords do you want? 3

Your generated password(s):
  1. k#9Tz{Qw2-Lb
  2. 7mP.xR4e@Vn!
  3. Hd5]uY&c8sA?

Generate more passwords? (y/n): n
Thanks for using the Password Generator. Stay safe!
```

## How it works

1. The user enters a length between 4 and 64.
2. The user picks which character types to include.
3. The program picks one character from each chosen type, so every type is present.
4. The rest of the password is filled with random characters from all chosen types.
5. The characters are shuffled so the guaranteed ones are not always at the start.

`random.SystemRandom()` is used instead of the default generator because it uses the operating system's secure random source, which is better suited for passwords.

## Project structure

```
task1-password-generator/
├── password_generator.py
└── README.md
```

## Author

Darshan, Auspify Internship