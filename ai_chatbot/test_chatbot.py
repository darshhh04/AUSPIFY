import json
import unittest
from datetime import datetime

from chatbot import INTENTS_FILE, Chatbot, SafeDict, format_number, safe_eval
from nlp_utils import Preprocessor, edit_distance, stem

FIXED_TIME = datetime(2026, 11, 12, 13, 45, 0)


def make_bot():
    return Chatbot(clock=lambda: FIXED_TIME)


class TestNlpTools(unittest.TestCase):
    def setUp(self):
        self.pre = Preprocessor({"python", "joke", "weather", "tell"})

    def test_tokenize_lowercases_and_removes_punctuation(self):
        self.assertEqual(self.pre.tokenize("What's UP?!"), ["what", "up"])

    def test_tokenize_expands_contractions(self):
        self.assertEqual(self.pre.tokenize("I can't go"), ["i", "can", "not", "go"])
        self.assertEqual(self.pre.tokenize("don't"), ["do", "not"])

    def test_stopwords_removed(self):
        self.assertEqual(
            self.pre.remove_stopwords(["tell", "me", "a", "joke"]), ["tell", "me", "joke"]
        )

    def test_stemming_joins_word_forms(self):
        self.assertEqual(stem("jokes"), stem("joke"))
        self.assertEqual(stem("telling"), stem("tell"))
        self.assertEqual(stem("making"), stem("make"))
        self.assertEqual(stem("studies"), "study")
        self.assertEqual(stem("is"), "is")

    def test_edit_distance(self):
        self.assertEqual(edit_distance("kitten", "sitting"), 3)
        self.assertEqual(edit_distance("pyhton", "python"), 1)  # swapped letters
        self.assertEqual(edit_distance("", "abc"), 3)
        self.assertEqual(edit_distance("same", "same"), 0)

    def test_spelling_is_corrected(self):
        self.assertEqual(self.pre.correct(["pyhton"]), ["python"])
        self.assertEqual(self.pre.correct(["wether"]), ["weather"])

    def test_unrelated_words_are_left_alone(self):
        self.assertEqual(self.pre.correct(["xyzzy"]), ["xyzzy"])
        self.assertEqual(self.pre.correct(["cat"]), ["cat"])   # too short to change

    def test_full_pipeline(self):
        self.assertEqual(self.pre.process("Tell me jokes, please!"), ["tell", "me", "jok"])


class TestSafeMath(unittest.TestCase):
    def test_basic_operations(self):
        self.assertEqual(safe_eval("2 + 3"), 5)
        self.assertEqual(safe_eval("5 + 3 * 2"), 11)
        self.assertEqual(safe_eval("(2 + 3) * 4"), 20)
        self.assertEqual(safe_eval("10 / 4"), 2.5)
        self.assertEqual(safe_eval("-3 + 5"), 2)
        self.assertEqual(safe_eval("6 x 7"), 42)

    def test_division_by_zero(self):
        with self.assertRaises(ZeroDivisionError):
            safe_eval("1 / 0")

    def test_dangerous_input_is_rejected(self):
        for bad in ("__import__('os')", "abs(-1)", "2 ** 3", "a + 1", "5 +"):
            with self.assertRaises(ValueError):
                safe_eval(bad)

    def test_number_formatting(self):
        self.assertEqual(format_number(84.0), "84")
        self.assertEqual(format_number(2.5), "2.5")
        self.assertEqual(format_number(0.1 + 0.2), "0.3")


class TestIntentFile(unittest.TestCase):
    def setUp(self):
        self.bot = make_bot()
        with open(INTENTS_FILE, encoding="utf-8") as f:
            self.raw = json.load(f)["intents"]

    def test_tags_are_unique(self):
        tags = [intent["tag"] for intent in self.raw]
        self.assertEqual(len(tags), len(set(tags)))

    def test_every_intent_has_responses(self):
        for intent in self.raw:
            if intent["tag"] != "more":  
                self.assertTrue(intent["responses"], intent["tag"])

    def test_special_intents_exist(self):
        for tag in ("fallback", "set_name", "more", "ask_name"):
            self.assertIn(tag, self.bot.intents)

    def test_no_placeholder_is_left_unfilled(self):
        for intent in self.raw:
            for response in intent["responses"]:
                self.assertNotIn("{", self.bot._fill(response), intent["tag"])

    def test_every_training_pattern_is_understood(self):
        for intent in self.raw:
            for pattern in intent["patterns"]:
                ranked = self.bot.classifier.rank(pattern)
                with self.subTest(pattern=pattern):
                    self.assertEqual(ranked[0][0], intent["tag"])
                    self.assertGreaterEqual(ranked[0][1], Chatbot.CONFIDENT)
                    if len(ranked) > 1:
                        self.assertLess(ranked[1][1], ranked[0][1] - 0.01)


class TestUnderstanding(unittest.TestCase):
    def setUp(self):
        self.bot = make_bot()

    def test_messages_map_to_the_right_intent(self):
        cases = [
            ("hello", "greeting"),
            ("hi there!", "greeting"),
            ("Good morning", "greeting"),
            ("bye", "goodbye"),
            ("see you later", "goodbye"),
            ("thanks a lot", "thanks"),
            ("thank you very much", "thanks"),
            ("how are you?", "how_are_you"),
            ("who are you", "bot_identity"),
            ("tell me about yourself", "bot_identity"),
            ("who made you", "creator"),
            ("how old are you", "bot_age"),
            ("what can you do", "help"),
            ("what time is it", "time"),
            ("can you tell me the time", "time"),
            ("what's the date today", "date"),
            ("what day is today", "date"),
            ("tell me a joke", "joke"),
            ("can you tell me a funny joke please", "joke"),
            ("tell me a joek", "joke"),             
            ("how do i learn python", "python_tips"),
            ("pyhton tips please", "python_tips"),  
            ("how can i study better", "study_tips"),
            ("motivate me", "motivation"),
            ("will it rain today", "weather"),
            ("i am so tired today", "feeling_bad"),
            ("you are awesome", "compliment"),
        ]
        for message, expected in cases:
            with self.subTest(message=message):
                self.assertEqual(self.bot.respond(message).intent, expected)

    def test_gibberish_gets_a_fallback(self):
        reply = self.bot.respond("blah blah xyzzy")
        self.assertEqual(reply.intent, "fallback")
        self.assertIn(reply.text, self.bot.intents["fallback"]["responses"])

    def test_extra_unknown_words_do_not_trigger_the_wrong_answer(self):
        reply = self.bot.respond("hello what is the capital of france")
        self.assertNotEqual(reply.intent, "greeting")

    def test_unsure_match_asks_a_clarifying_question(self):
        reply = self.bot.respond("tel me a joek")
        self.assertEqual(reply.intent, "clarify")
        self.assertIn("a joke", reply.text)

    def test_empty_message(self):
        reply = self.bot.respond("    ")
        self.assertEqual(reply.intent, "empty")
        self.assertEqual(self.bot.history, [])

    def test_very_long_message_does_not_crash(self):
        reply = self.bot.respond("hello " * 500)
        self.assertIsNotNone(reply.text)


class TestBehaviour(unittest.TestCase):
    def setUp(self):
        self.bot = make_bot()

    def test_time_and_date_use_the_clock(self):
        self.assertIn("1:45 PM", self.bot.respond("what time is it").text)
        self.assertIn("Thursday, 12 November 2026", self.bot.respond("what is the date today").text)

    def test_maths(self):
        self.assertEqual(self.bot.respond("calculate 12 * 7").text, "12 * 7 = 84")
        self.assertIn("2.5", self.bot.respond("what is 10 / 4").text)
        self.assertIn("11", self.bot.respond("5 + 3 * 2").text)
        self.assertEqual(self.bot.respond("12 x 3").intent, "math")

    def test_divide_by_zero_message(self):
        reply = self.bot.respond("10 / 0")
        self.assertEqual(reply.intent, "math")
        self.assertIn("zero", reply.text)

    def test_numbers_and_dates_are_not_maths(self):
        self.assertNotEqual(self.bot.respond("what is 7").intent, "math")
        self.assertNotEqual(self.bot.respond("2026-11-12").intent, "math")
        self.assertNotEqual(self.bot.respond("2 ** 3").intent, "math")

    def test_remembers_the_users_name(self):
        self.assertIn("don't know your name", self.bot.respond("what is my name").text)

        reply = self.bot.respond("my name is priya")
        self.assertEqual(reply.intent, "set_name")
        self.assertEqual(self.bot.user_name, "Priya")

        self.assertIn(", Priya", self.bot.respond("hello").text)
        self.assertIn("Priya", self.bot.respond("what is my name").text)

    def test_call_me_also_sets_the_name(self):
        self.bot.respond("call me Ravi")
        self.assertEqual(self.bot.user_name, "Ravi")

    def test_another_one_repeats_the_last_topic(self):
        first = self.bot.respond("tell me a joke")
        second = self.bot.respond("another one")
        self.assertEqual(second.intent, "joke")
        self.assertNotEqual(first.text, second.text)

    def test_another_one_without_context(self):
        reply = self.bot.respond("another one")
        self.assertEqual(reply.intent, "more")
        self.assertIn("More of what", reply.text)

        self.bot.respond("tell me a joke")
        self.bot.respond("hello")                   
        self.assertIn("More of what", self.bot.respond("one more").text)

    def test_same_answer_is_not_repeated_back_to_back(self):
        previous = None
        for _ in range(25):
            text = self.bot.respond("tell me a joke").text
            self.assertNotEqual(text, previous)
            previous = text

    def test_history_is_recorded(self):
        self.bot.respond("hello")
        self.assertEqual(len(self.bot.history), 2)
        self.assertEqual(self.bot.history[0][1], "You")
        self.assertEqual(self.bot.history[1][1], self.bot.name)

    def test_reset_forgets_everything(self):
        self.bot.respond("my name is Priya")
        self.bot.respond("tell me a joke")
        self.bot.reset()
        self.assertIsNone(self.bot.user_name)
        self.assertIsNone(self.bot.last_tag)
        self.assertEqual(self.bot.history, [])

    def test_unknown_placeholder_is_left_alone(self):
        self.assertEqual("{nothing}".format_map(SafeDict()), "{nothing}")


if __name__ == "__main__":
    unittest.main()