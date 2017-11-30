import io
import os
# changed this line from import simplejson to import json assimplejson
import json as simplejson
import six
from builtins import object
# Describes where to search for the config file if no location is specified
from typing import Text

DEFAULT_CONFIG_LOCATION = "config.json"

DEFAULT_CONFIG = {
    "project": None,
    "fixed_model_name": None,
    "config": DEFAULT_CONFIG_LOCATION,
    "data": None,
    "emulate": None,
    "language": "en",
    "log_file": None,
    "log_level": 'INFO',
    "mitie_file": os.path.join("data", "total_word_feature_extractor.dat"),
    "spacy_model_name": None,
    "num_threads": 1,
    "max_training_processes": 1,
    "path": "projects",
    "port": 5000,
    "token": None,
    "cors_origins": [],
    "max_number_of_ngrams": 7,
    "pipeline": [],
    "response_log": "logs",
    "aws_endpoint_url": None,
    "duckling_dimensions": None,
    "duckling_http_url": None,
    "ner_crf": {
        "BILOU_flag": True,
        "features": [
            ["low", "title", "upper", "pos", "pos2"],
            ["bias", "low", "word3", "word2", "upper", "title", "digit", "pos", "pos2", "pattern"],
            ["low", "title", "upper", "pos", "pos2"]],
        "max_iterations": 50,
        "L1_c": 1,
        "L2_c": 1e-3
    },
    "intent_classifier_sklearn": {
        "C": [1, 2, 5, 10, 20, 100],
        "kernel": "linear"
    }
}


class RasaNLUConfig(object):
    DEFAULT_PROJECT_NAME = "default"
    def __init__(self, filename=None, env_vars=None, cmdline_args=None):

        self.override(DEFAULT_CONFIG)
        if filename is not None:
            try:
                with io.open(filename, encoding='utf-8') as f:
                    file_config = simplejson.loads(f.read())
            except ValueError as e:
                raise InvalidConfigError("Failed to read configuration file '{}'. Error: {}".format(filename, e))
            self.override(file_config)

        if isinstance(self.__dict__['pipeline'], six.string_types):
            from rasa_nlu import registry
            if self.__dict__['pipeline'] in registry.registered_pipeline_templates:
                self.__dict__['pipeline'] = registry.registered_pipeline_templates[self.__dict__['pipeline']]
            else:
                raise InvalidConfigError("No pipeline specified and unknown pipeline template " +
                                         "'{}' passed. Known pipeline templates: {}".format(
                                                 self.__dict__['pipeline'],
                                                 ", ".join(registry.registered_pipeline_templates.keys())))

        for key, value in self.items():
            setattr(self, key, value)

    def __getitem__(self, key):
        return self.__dict__[key]

    def get(self, key, default=None):
        return self.__dict__.get(key, default)

    def __setitem__(self, key, value):
        self.__dict__[key] = value

    def __delitem__(self, key):
        del self.__dict__[key]

    def __contains__(self, key):
        return key in self.__dict__

    def __len__(self):
        return len(self.__dict__)

    def __getstate__(self):
        return self.as_dict()

    def __setstate__(self, state):
        self.override(state)

    def items(self):
        return list(self.__dict__.items())

    def as_dict(self):
        return dict(list(self.items()))

    def view(self):
        return simplejson.dumps(self.__dict__, indent=4)

    def split_arg(self, config, arg_name):
        if arg_name in config and isinstance(config[arg_name], six.string_types):
            config[arg_name] = config[arg_name].split(",")
        return config

    def split_pipeline(self, config):
        if "pipeline" in config and isinstance(config["pipeline"], six.string_types):
            config = self.split_arg(config, "pipeline")
            if "pipeline" in config and len(config["pipeline"]) == 1:
                config["pipeline"] = config["pipeline"][0]
        return config

    def make_paths_absolute(self, config, keys):
        abs_path_config = dict(config)
        for key in keys:
            if key in abs_path_config and abs_path_config[key] is not None and not os.path.isabs(abs_path_config[key]):
                abs_path_config[key] = os.path.join(os.getcwd(), abs_path_config[key])
        return abs_path_config

    # noinspection PyCompatibility
    def make_unicode(self, config):
        if six.PY2:
            # Sometimes (depending on the source of the config value) an argument will be str instead of unicode
            # to unify that and ease further usage of the config, we convert everything to unicode
            for k, v in config.items():
                if type(v) is str:
                    config[k] = unicode(v, "utf-8")
        return config

    def override(self, config):
        abs_path_config = self.make_unicode(self.make_paths_absolute(config, ["path", "response_log"]))
        self.__dict__.update(abs_path_config)
