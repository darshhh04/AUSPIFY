# AI Chatbot Application

**Auspify Internship | Task 6 (Advanced)**

An interactive chatbot with a chat window, written in Python. It reads what the user types, uses basic NLP to work out what they mean, and replies with a suitable answer.

It is an **intent-based chatbot**: it matches messages against example sentences and picks a response. It does not use an external AI service, and it needs no extra libraries.

## What it does

- Chat window with message bubbles, timestamps and a "typing..." status
- Understands greetings, goodbyes, thanks, small talk, questions about the bot and more
- Gives jokes, Python tips, study tips and motivation
- Tells the current time and date
- Solves simple maths, like `calculate 12 * 7`
- Remembers your name when you say `my name is ...`
- Handles spelling mistakes, for example `pyhton tips` still works
- Understands follow-ups: after a joke, `another one` gives a new joke
- Asks a clarifying question when it is not sure, instead of guessing
- Saves the conversation to a text file
- A "Show intent" switch shows what the bot understood and how confident it was

## Skills used

- Object-Oriented Programming (`Preprocessor`, `IntentClassifier`, `Chatbot`, `ChatApp`)
- NLP fundamentals (tokenization, stop words, stemming, TF-IDF, cosine similarity)
- Python libraries (`json`, `re`, `ast`, `collections`, `math`, `tkinter`)
- AI application development (intent classification, confidence handling, context)

## How it works

Each message goes through these steps:

1. **Tokenize:** lowercase the text, expand contractions (`what's` becomes `what`) and split into words.
2. **Fix spelling:** a word the bot has never seen is replaced by the closest known word, using edit distance (this also catches swapped letters like `pyhton`).
3. **Remove stop words:** drop very common words such as `the` and `a`.
4. **Stem:** cut word endings so `jokes`, `joke` and `joking` match.
5. **Match the intent:** every example sentence in `intents.json` is turned into a TF-IDF vector. The message is turned into a vector the same way, and cosine similarity finds the closest example.
6. **Decide:**
   - score at or above 0.60: answer directly
   - score between 0.30 and 0.60: ask "Are you asking about ...?"
   - lower: use a fallback reply

Before step 1, the bot checks two special cases: a name ("my name is ...") and a plain maths expression. Maths is solved with a safe parser, not `eval`.

## How to run

1. Make sure Python 3.8 or higher is installed.
2. Open a terminal in this folder.
3. Run:

```bash
python chat_app.py
```

On Linux, install Tkinter with `sudo apt install python3-tk` if it is missing.

## Things to try

| Type this | What happens |
|-----------|--------------|
| `hello` | Greeting |
| `my name is Darshan` | Bot remembers your name and uses it later |
| `tell me a joke`, then `another one` | A new joke each time |
| `calculate 12 * 7` | `12 * 7 = 84` |
| `what time is it` | Current time |
| `how do i learn pyhton` | Python tip, even with the typo |
| `tel me a joek` | Asks "Are you asking about a joke?" |
| `blah blah` | Fallback reply |
| `help` | List of things the bot can do |

## Sample conversation

```
Sage: Hi! I'm Sage. Ask me anything, or type 'help' to see what I can do.
You:  hello
Sage: Hello! How can I help you today?
You:  my name is Darshan
Sage: Nice to meet you, Darshan! I'll remember your name.
You:  tell me a joke
Sage: There are 10 types of people: those who understand binary and those who don't.
You:  another one
Sage: Debugging: being the detective in a crime movie where you are also the murderer.
You:  calculate 12 * 7
Sage: 12 * 7 = 84
You:  tel me a joek
Sage: I'm not sure I understood. Are you asking about a joke?
You:  thanks
Sage: Anytime, Darshan! Anything else I can do?
You:  bye
Sage: Goodbye, Darshan! Come back anytime.
```

## Adding new topics

All the bot's knowledge is in `intents.json`, so no code changes are needed. Add a block like this:

```json
{
    "tag": "hobbies",
    "description": "hobbies",
    "patterns": ["what are your hobbies", "what do you do for fun"],
    "responses": ["I like chatting and counting words."]
}
```

- `patterns` are example sentences the user might type
- `responses` are possible answers (the bot picks one and avoids repeating the last one)
- `description` is used in the "Are you asking about ...?" question
- `"repeatable": true` lets the user say "another one"
- Placeholders you can use in responses: `{name_part}`, `{user_name}`, `{bot_name}`, `{time}`, `{date}`

Then run the tests. One test checks that every example sentence points to its own intent, so it will warn you if a new topic is too similar to an old one.

## Testing

```bash
python -m unittest -v
```

The 35 tests cover tokenizing, stemming, spelling correction, maths safety, intent matching, the intents file, name memory, follow-ups and the clarifying question.

## Limits

- The bot only knows the topics in `intents.json`. It cannot answer general knowledge questions.
- It does not use live data such as real weather.
- A message with many unknown words gets a low score on purpose, so it falls back instead of giving a wrong answer.

## Project structure

```
task6-ai-chatbot/
├── chat_app.py        (the chat window)
├── chatbot.py         (intent matching, maths, chatbot logic)
├── nlp_utils.py       (tokenizing, stemming, spelling correction)
├── intents.json       (topics, example sentences and responses)
├── test_chatbot.py    (unit tests)
└── README.md
```

## Author

Darshan, Auspify Internship