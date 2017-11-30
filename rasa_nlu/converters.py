import io
import json


from rasa_nlu.training_data import TrainingData, Message

RASA_FILE_FORMAT = "rasa_nlu"

def load_data(filename):
    # type: (Text) -> TrainingData
    """Loads training data stored in the rasa NLU data format."""

    with io.open(filename, encoding="utf-8-sig") as f:
        data = json.loads(f.read())


    common = data['rasa_nlu_data'].get("common_examples", list())
    intent = data['rasa_nlu_data'].get("intent_examples", list())
    entity = data['rasa_nlu_data'].get("entity_examples", list())
    regex_features = data['rasa_nlu_data'].get("regex_features", list())
    synonyms = data['rasa_nlu_data'].get("entity_synonyms", list())
    entity_synonyms = get_entity_synonyms_dict(synonyms)


    all_examples = common + intent + entity
    training_examples = []
    for e in all_examples:
        data = e.copy()
        if "text" in data:
            del data["text"]
        training_examples.append(Message(e["text"], data))

    return TrainingData(training_examples, entity_synonyms, regex_features)


def get_entity_synonyms_dict(synonyms):
    # type: (List[Dict]) -> Dict
    """build entity_synonyms dictionary"""
    entity_synonyms = {}
    for s in synonyms:
        if "value" in s and "synonyms" in s:
            for synonym in s["synonyms"]:
                entity_synonyms[synonym] = s["value"]
    return entity_synonyms


