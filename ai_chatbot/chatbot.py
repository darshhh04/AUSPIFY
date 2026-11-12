import ast
import json
import math
import operator
import os
import random
import re
from collections import Counter, namedtuple
from datetime import datetime

from nlp_utils import Preprocessor

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INTENTS_FILE = os.path.join(BASE_DIR, "intents.json")

MAX_INPUT = 300  

Reply = namedtuple("Reply", ["text", "intent", "confidence"])

OPERATORS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Mod: operator.mod,
}

MATH_PATTERN = re.compile(
    r"(?:calculate|compute|solve|evaluate|what is|what's|whats)?\s*"
    r"([\d\s+\-*/x×÷%().]+?)\s*[?=]?",
    re.IGNORECASE,
)


def _evaluate(node):
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in OPERATORS:
        return OPERATORS[type(node.op)](_evaluate(node.left), _evaluate(node.right))
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _evaluate(node.operand)
        return -value if isinstance(node.op, ast.USub) else value
    raise ValueError("Unsupported expression")


def safe_eval(expression):
    expression = expression.replace("x", "*").replace("×", "*").replace("÷", "/")
    try:
        tree = ast.parse(expression.strip(), mode="eval")
    except SyntaxError:
        raise ValueError("Not a valid expression")
    return _evaluate(tree.body)


def format_number(value):
    if not math.isfinite(value):
        raise OverflowError("Number too large")
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    return f"{value:.10g}"


class SafeDict(dict):

    def __missing__(self, key):
        return "{" + key + "}"


class IntentClassifier:

    UNKNOWN_WEIGHT = 1.0  

    def __init__(self, intents):
        patterns = [
            (intent["tag"], pattern)
            for intent in intents
            for pattern in intent.get("patterns", [])
        ]

        base = Preprocessor()
        vocabulary = set()
        for _, pattern in patterns:
            vocabulary.update(base.tokenize(pattern))
        self.preprocessor = Preprocessor(vocabulary)

        documents = [
            (tag, self.preprocessor.process(pattern, correct=False))
            for tag, pattern in patterns
        ]

        self.idf = self._build_idf([tokens for _, tokens in documents])
        self.unknown_weight = max(self.idf.values()) * self.UNKNOWN_WEIGHT
        self.vectors = [(tag, self._vectorize(tokens)) for tag, tokens in documents]

    @staticmethod
    def _build_idf(documents):
        total = len(documents)
        counts = Counter(term for tokens in documents for term in set(tokens))
        return {
            term: math.log((1 + total) / (1 + count)) + 1
            for term, count in counts.items()
        }

    def _vectorize(self, tokens, is_query=False):
        vector = {}
        for term, count in Counter(tokens).items():
            if term in self.idf:
                vector[term] = count * self.idf[term]
            elif is_query:
                vector[term] = count * self.unknown_weight

        length = math.sqrt(sum(weight * weight for weight in vector.values()))
        if not length:
            return {}
        return {term: weight / length for term, weight in vector.items()}

    def rank(self, text):
        query = self._vectorize(self.preprocessor.process(text), is_query=True)

        best = {}
        for tag, vector in self.vectors:
            score = sum(weight * vector.get(term, 0.0) for term, weight in query.items())
            if score > best.get(tag, 0.0):
                best[tag] = score
        return sorted(best.items(), key=lambda item: item[1], reverse=True)


class Chatbot:
    CONFIDENT = 0.60   
    UNSURE = 0.30      

    def __init__(self, intents_file=INTENTS_FILE, name="Sage", clock=None):
        with open(intents_file, encoding="utf-8") as f:
            data = json.load(f)

        self.intents = {intent["tag"]: intent for intent in data["intents"]}
        self.classifier = IntentClassifier(list(self.intents.values()))
        self.name = name
        self.clock = clock or datetime.now

        self.user_name = None
        self.last_tag = None     
        self.last_reply = {}     
        self.history = []         

    def greeting(self):
        return f"Hi! I'm {self.name}. Ask me anything, or type 'help' to see what I can do."

    def reset(self):
        self.user_name = None
        self.last_tag = None
        self.last_reply = {}
        self.history = []

    def respond(self, text):
        text = " ".join(text.split())[:MAX_INPUT]
        if not text:
            return Reply("Please type a message and I'll do my best to help.", "empty", 0.0)

        self._log("You", text)
        reply = self._try_name(text) or self._try_math(text) or self._answer_intent(text)
        self._log(self.name, reply.text)
        return reply


    def _try_name(self, text):
        match = re.search(
            r"\b(?:my name is|call me|i am called)\s+([a-z][a-z'-]{0,19})\b",
            text, re.IGNORECASE,
        )
        if not match:
            return None
        self.user_name = match.group(1).capitalize()
        self.last_tag = None
        return Reply(self._fill(self._pick("set_name")), "set_name", 1.0)

    def _try_math(self, text):
        match = MATH_PATTERN.fullmatch(text.strip())
        if not match:
            return None

        expression = match.group(1).strip()
        if not re.search(r"\d\s*[-+*/x×÷%]\s*[\d(]", expression):
            return None  # just a number, not a calculation
        if re.fullmatch(r"\d{1,4}[-/]\d{1,2}[-/]\d{1,4}", expression):
            return None  

        try:
            result = safe_eval(expression)
            answer = f"{expression} = {format_number(result)}"
        except ZeroDivisionError:
            answer = "I can't divide by zero. Nobody can!"
        except OverflowError:
            answer = "That number is too big for me."
        except ValueError:
            return None

        self.last_tag = None
        return Reply(answer, "math", 1.0)

    def _answer_intent(self, text):
        ranked = self.classifier.rank(text)
        tag, score = ranked[0] if ranked else (None, 0.0)

        if tag and score >= self.CONFIDENT:
            return self._build_reply(tag, score)

        if tag and score >= self.UNSURE and self.intents[tag].get("description"):
            description = self.intents[tag]["description"]
            return Reply(
                f"I'm not sure I understood. Are you asking about {description}?",
                "clarify", score,
            )

        self.last_tag = None
        return Reply(self._pick("fallback"), "fallback", score)


    def _build_reply(self, tag, score):
        if tag == "more":
            if not self.last_tag:
                return Reply("More of what? Ask me for a joke or a tip first.", "more", score)
            tag = self.last_tag
        else:
            self.last_tag = tag if self.intents[tag].get("repeatable") else None

        if tag == "ask_name" and not self.user_name:
            text = "I don't know your name yet. Tell me with 'my name is ...'."
        else:
            text = self._fill(self._pick(tag))
        return Reply(text, tag, score)

    def _pick(self, tag):
        """Choose a response, avoiding the one used last time."""
        options = self.intents[tag]["responses"]
        previous = self.last_reply.get(tag)
        choices = [option for option in options if option != previous] or options
        choice = random.choice(choices)
        self.last_reply[tag] = choice
        return choice

    def _fill(self, template):
        now = self.clock()
        values = SafeDict(
            time=now.strftime("%I:%M %p").lstrip("0"),
            date=now.strftime("%A, %d %B %Y"),
            bot_name=self.name,
            user_name=self.user_name or "friend",
            name_part=f", {self.user_name}" if self.user_name else "",
        )
        return template.format_map(values)

    def _log(self, speaker, text):
        self.history.append((self.clock().strftime("%H:%M:%S"), speaker, text))