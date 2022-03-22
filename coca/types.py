from __future__ import annotations

from dataclasses import dataclass, field

from stanza import Pipeline

dependency_parser = Pipeline(lang="en", processors="tokenize,mwt,pos,lemma,depparse", tokenize_pretokenized=True)


@dataclass
class Sentence:
    tokens: list[str] = field(init=True)
    skipped: bool = field(default=True, init=False)
    dependency: list | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        self.skipped = "@" in self.tokens

        if not self.skipped:
            self.dependency = dependency_parser(' '.join(self.tokens))


@dataclass
class Paragraph:
    sentences: list[Sentence] = field(init=True)


@dataclass
class Text:
    text_id: str = field(init=True)
    paragraphs: list[Paragraph] = field(init=True)
