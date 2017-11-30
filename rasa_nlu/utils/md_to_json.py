from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import re
import io
from rasa_nlu.training_data import Message

ent_regex = re.compile('\[(?P<value>[^\]]+)]'
                       '\((?P<entity>[^:)]+)\)')  # [restaurant](what)
ent_regex_with_value = re.compile('\[(?P<synonym>[^\]]+)'
                                  '\]\((?P<entity>\w*?):'
                                  '(?P<value>[^)]+)\)')  # [open](open:1)
intent_regex = re.compile('##\s*intent:(.+)')
synonym_regex = re.compile('##\s*synonym:(.+)')
example_regex = re.compile('\s*-\s*(.+)')

INTENT_PARSING_STATE = "intent"
SYNONYM_PARSING_STATE = "synonym"


class MarkdownToJson(object):
    """Converts training examples written in md to standard rasa json format."""

    def __init__(self, file_name):
        self.file_name = file_name
        # set when parsing examples from a given intent
        self.current_intent = None
        self.common_examples = []
        self.entity_synonyms = []
        self.load()

    def load(self):
        """Parse the content of the actual .md file."""

        with io.open(self.file_name, 'rU', encoding="utf-8-sig") as f:
            for row in f:
                intent_match = re.search(intent_regex, row)
                if intent_match is not None:
                    self._set_current_state(
                            INTENT_PARSING_STATE, intent_match.group(1))
                    continue

                synonym_match = re.search(synonym_regex, row)
                if synonym_match is not None:
                    self._set_current_state(
                            SYNONYM_PARSING_STATE, synonym_match.group(1))
                    continue

                self._parse_intent_or_synonym_example(row)
        return {
            "rasa_nlu_data": {
                "common_examples": self.common_examples,
                "entity_synonyms": self.entity_synonyms
            }
        }

    def _parse_intent_or_synonym_example(self, row):
        example_match = re.finditer(example_regex, row)
        for matchIndex, match in enumerate(example_match):
            example_line = match.group(1)
            if self._current_state() == INTENT_PARSING_STATE:
                parsed = self._parse_intent_example(example_line)
                self.common_examples.append(parsed)
            else:
                self.entity_synonyms[-1]['synonyms'].append(example_line)

    def _parse_intent_example(self, example_in_md):
        entities = []
        utter = example_in_md
        for regex in [ent_regex, ent_regex_with_value]:
            utter = re.sub(regex, r"\1", utter)  # [text](entity) -> text
            ent_matches = re.finditer(regex, example_in_md)
            for matchNum, match in enumerate(ent_matches):
                if 'synonym' in match.groupdict():
                    entity_value_in_utter = match.groupdict()['synonym']
                else:
                    entity_value_in_utter = match.groupdict()['value']

                start_index = utter.index(entity_value_in_utter)
                end_index = start_index + len(entity_value_in_utter)

                entities.append({
                    'entity': match.groupdict()['entity'],
                    'value': match.groupdict()['value'],
                    'start': start_index,
                    'end': end_index
                })

        message = Message(utter, {'intent': self.current_intent})
        if len(entities) > 0:
            message.set('entities', entities)
        return message

    def _set_current_state(self, state, value):
        """Switch between 'intent' and 'synonyms' mode."""

        if state == INTENT_PARSING_STATE:
            self.current_intent = value
        elif state == SYNONYM_PARSING_STATE:
            self.current_intent = None
            self.entity_synonyms.append({'value': value, 'synonyms': []})
        else:
            raise ValueError("State must be either '{}' or '{}'".format(
                    INTENT_PARSING_STATE, SYNONYM_PARSING_STATE))

    def _current_state(self):
        """Informs whether we are currently loading intents or synonyms."""

        if self.current_intent is not None:
            return INTENT_PARSING_STATE
        else:
            return SYNONYM_PARSING_STATE
