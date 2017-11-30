# import logging
# import os
# import shutil
# import tarfile
# from builtins import object
# from rasa_nlu.config import RasaNLUConfig
# from typing import Optional, Tuple, List
# from typing import Text
#
# logger = logging.getLogger(__name__)
#
#
# def get_persistor(config):
#     # type: (RasaNLUConfig) -> Optional[Persistor]
#     """Returns an instance of the requested persistor.
#
#     Currently, `aws` and `gcs` are supported"""
#
#     if 'storage' not in config:
#         raise KeyError("No persistent storage specified. Supported values "
#                        "are {}".format(", ".join(['aws', 'gcs'])))
#
#     if config['storage'] == 'aws':
#         return AWSPersistor(config['aws_region'], config['bucket_name'],
#                             config['aws_endpoint_url'])
#     elif config['storage'] == 'gcs':
#         return GCSPersistor(config['bucket_name'])
#     else:
#         return None
#
#
# class Persistor(object):
#     """Store models in cloud and fetch them when needed"""
#
#     def persist(self, mode_directory, model_name, project):
#         # type: (Text) -> None
#         """Uploads a model persisted in the `target_dir` to cloud storage."""
#
#         if not os.path.isdir(mode_directory):
#             raise ValueError("Target directory '{}' not "
#                              "found.".format(mode_directory))
#
#         file_key, tar_path = self._compress(mode_directory, model_name, project)
#         self._persist_tar(file_key, tar_path)
#
#     def retrieve(self, model_name, project, target_path):
#         # type: (Text) -> None
#         """Downloads a model that has been persisted to cloud storage."""
#
#         tar_name = self._tar_name(model_name, project)
#
#         self._retrieve_tar(tar_name)
#         self._decompress(tar_name, target_path)
#
#     def list_models(self, project):
#         # type: (Text) -> List[Text]
#         """Lists all the trained models of a project."""
#
#         raise NotImplementedError
#
#     def _retrieve_tar(self, filename):
#         # type: (Text) -> Text
#         """Downloads a model previously persisted to cloud storage."""
#
#         raise NotImplementedError("")
#
#     def _persist_tar(self, filekey, tarname):
#         # type: (Text, Text) -> None
#         """Uploads a model persisted in the `target_dir` to cloud storage."""
#
#         raise NotImplementedError("")
#
#     def _compress(self, model_directory, model_name, project):
#         # type: (Text) -> Tuple[Text, Text]
#         """Creates a compressed archive and returns key and tar."""
#
#         base_name = self._tar_name(model_name, project, include_extension=False)
#         tar_name = shutil.make_archive(base_name, 'gztar',
#                                        root_dir=model_directory,
#                                        base_dir=".")
#         file_key = os.path.basename(tar_name)
#         return file_key, tar_name
#
#     @staticmethod
#     def _project_prefix(project):
#         # type: (Text) -> Text
#
#         return '{}___'.format(project or RasaNLUConfig.DEFAULT_PROJECT_NAME)
#
#     @staticmethod
#     def _project_and_model_from_filename(filename):
#         # type: (Text) -> Text
#
#         split = filename.split("___")
#         if len(split) > 1:
#             model_name = split[1].replace(".tar.gz", "")
#             return split[0], model_name
#         else:
#             return split[0], ""
#
#     @staticmethod
#     def _tar_name(model_name, project, include_extension=True):
#         # type: (Text, Text, bool) -> Text
#
#         ext = ".tar.gz" if include_extension else ""
#         return '{p}{m}{ext}'.format(p=Persistor._project_prefix(project),
#                                     m=model_name, ext=ext)
#
#     @staticmethod
#     def _decompress(compressed_path, target_path):
#         # type: (Text, Text) -> None
#
#         with tarfile.open(compressed_path, "r:gz") as tar:
#             tar.extractall(target_path)
#
#
#
#
#
