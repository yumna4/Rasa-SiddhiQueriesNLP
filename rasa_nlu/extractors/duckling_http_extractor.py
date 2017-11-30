from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

import io
import logging
import os

import requests
import simplejson
from builtins import str
from typing import Any, Dict
from typing import List
from typing import Optional
from typing import Text

from rasa_nlu.config import RasaNLUConfig
from rasa_nlu.extractors import EntityExtractor
from rasa_nlu.model import Metadata
from rasa_nlu.training_data import Message

logger = logging.getLogger(__name__)


class DucklingHTTPExtractor(EntityExtractor):
    """Searches for structured entites, e.g. dates, using a duckling server."""

    name = "ner_duckling_http"

    provides = ["entities"]

    def __init__(self, duckling_url, language, dimensions=None):
        # type: (Text, Optional[List[Text]]) -> None

        super(DucklingHTTPExtractor, self).__init__()
        self.dimensions = dimensions
        self.duckling_url = duckling_url
        self.language = language

    @classmethod
    def create(cls, config):
        # type: (RasaNLUConfig) -> DucklingHTTPExtractor

        return DucklingHTTPExtractor(config["duckling_http_url"],
                                     config["language"],
                                     config["duckling_dimensions"])

    def _duckling_parse(self, text):
        """Sends the request to the duckling server and parses the result."""

        payload = {"text": text, "lang": self.language}
        response = requests.post(self.duckling_url + "/parse", data=payload)
        if response.status_code == 200:
            return simplejson.loads(response.text)
        else:
            logger.warn("Failed to get a proper response from remote duckling. "
                        "Status Code: {}. ".format(response.status_code) +
                        "Response: {}".format(response.text))
            return {}

    def _filter_irrelevant_matches(self, matches):
        """Only return dimensions the user configured"""

        if self.dimensions:
            return [match
                    for match in matches
                    if match["dim"] in self.dimensions]
        else:
            return matches

    def process(self, message, **kwargs):
        # type: (Message, **Any) -> None

        extracted = []
        if self.duckling_url is not None:

            matches = self._duckling_parse(message.text)
            relevant_matches = self._filter_irrelevant_matches(matches)
            for match in relevant_matches:
                entity = {
                    "start": match["start"],
                    "end": match["end"],
                    "text": match["body"],
                    "value": match["value"]["value"],
                    "additional_info": match["value"],
                    "entity": match["dim"]}

                extracted.append(entity)

        extracted = self.add_extractor_name(extracted)
        message.set("entities",
                    message.get("entities", []) + extracted,
                    add_to_output=True)

    def persist(self, model_dir):
        # type: (Text) -> Dict[Text, Any]

        file_name = self.name + ".json"
        with io.open(os.path.join(model_dir, file_name), 'w') as f:
            dumped = str(simplejson.dumps({"dimensions": self.dimensions}))
            f.write(dumped)
        return {self.name: file_name}

    @classmethod
    def load(cls,
             model_dir=None,  # type: Text
             model_metadata=None,  # type: Metadata
             cached_component=None,  # type: Optional[DucklingHTTPExtractor]
             **kwargs  # type: **Any
             ):
        # type: (...) -> DucklingHTTPExtractor

        persisted = os.path.join(model_dir, model_metadata.get(cls.name))
        config = kwargs.get("config", {})
        dimensions = None

        if os.path.isfile(persisted):
            with io.open(persisted, encoding='utf-8') as f:
                persisted_data = simplejson.loads(f.read())
                dimensions = persisted_data["dimensions"]

        return DucklingHTTPExtractor(config.get("duckling_http_url"),
                                     model_metadata.get("language"),
                                     dimensions)
