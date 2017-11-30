# -*- coding: utf-8 -*-
import io
import json
import logging
import os

from builtins import object, str
from collections import defaultdict

from rasa_nlu.utils.json_to_md import JsonToMd


from rasa_nlu.utils import lazyproperty, ordered


logger = logging.getLogger(__name__)


class Message(object):
    def __init__(self, text, data=None, output_properties=None, time=None):
        self.text = text
        self.time = time
        self.data = data if data else {}
        self.output_properties = output_properties if output_properties else set()

    def set(self, prop, info, add_to_output=False):
        self.data[prop] = info
        if add_to_output:
            self.output_properties.add(prop)

    def get(self, prop, default=None):
        return self.data.get(prop, default)

    def as_dict(self, only_output_properties=False):
        if only_output_properties:
            d = {key: value for key, value in self.data.items() if key in self.output_properties}
        else:
            d = self.data
        return dict(d, text=self.text)


class TrainingData(object):
    """Holds loaded intent and entity training data."""

    # Validation will ensure and warn if these lower limits are not met
    MIN_EXAMPLES_PER_INTENT = 2
    MIN_EXAMPLES_PER_ENTITY = 2

    def __init__(self, training_examples=None, entity_synonyms=None, regex_features=None):
        # type: (Optional[List[Message]], Optional[Dict[Text, Text]]) -> None

        self.training_examples = self.sanitice_examples(training_examples) if training_examples else []
        self.entity_synonyms = entity_synonyms if entity_synonyms else {}
        self.regex_features = regex_features if regex_features else []


    def sanitice_examples(self, examples):
        # type: (List[Message]) -> List[Message]
        """Makes sure the training data is cleaned, e.q. removes trailing whitespaces from intent annotations."""

        for e in examples:
            if e.get("intent") is not None:
                e.set("intent", e.get("intent").strip())
        return examples

    @lazyproperty
    def intent_examples(self):
        # type: () -> List[Message]
        return [e for e in self.training_examples if e.get("intent") is not None]

    @lazyproperty
    def entity_examples(self):
        # type: () -> List[Message]
        return [e for e in self.training_examples if e.get("entities") is not None]

    @lazyproperty
    def num_entity_examples(self):
        # type: () -> int
        """Returns the number of proper entity training examples (containing at least one annotated entity)."""

        return len([e for e in self.training_examples if len(e.get("entities", [])) > 0])

    @lazyproperty
    def num_intent_examples(self):
        # type: () -> int
        """Returns the number of intent examples."""

        return len(self.intent_examples)

    def as_json(self, **kwargs):
        # type: (**Any) -> str
        """Represent this set of training examples as json adding the passed meta information."""

        js_entity_synonyms = defaultdict(list)
        for k, v in self.entity_synonyms.items():
            if k != v:
                js_entity_synonyms[v].append(k)

        return str(json.dumps({
            "rasa_nlu_data": {
                "common_examples": [example.as_dict() for example in self.training_examples],
                "regex_features": self.regex_features,
                "entity_synonyms": [{'value': value, 'synonyms': syns} for value, syns in js_entity_synonyms.items()]
            }
        }, **kwargs))

    def as_markdown(self, **kwargs):
        # type: (**Any) -> str
        """Represent this set of training examples as markdown adding the passed meta information."""

        return JsonToMd(self.training_examples, self.entity_synonyms).to_markdown()

    def persist(self, dir_name):
        # type: (Text) -> Dict[Text, Any]
        """Persists this training data to disk and returns necessary information to load it again."""

        data_file = os.path.join(dir_name, "training_data.json")
        with io.open(data_file, 'w') as f:
            f.write(self.as_json(indent=2))

        return {
            "training_data": "training_data.json"
        }

    def sorted_entity_examples(self):
        # type: () -> List[Message]
        """Sorts the entity examples by the annotated entity."""

        return sorted([entity for ex in self.entity_examples for entity in ex.get("entities")],
                      key=lambda e: e["entity"])

    def sorted_intent_examples(self):
        # type: () -> List[Message]
        """Sorts the intent examples by the name of the intent."""

        return sorted(self.intent_examples, key=lambda e: e.get("intent"))