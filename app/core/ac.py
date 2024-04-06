import ahocorasick

from app.models import Keyword

automaton = ahocorasick.Automaton()


def init_automaton(keywords: list[Keyword]):
    for keyword in keywords:
        automaton.add_word(keyword.keyword, (keyword.id, keyword.keyword))
    automaton.make_automaton()
