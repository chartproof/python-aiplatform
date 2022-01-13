# -*- coding: utf-8 -*-

# Copyright 2021 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import datetime
from typing import Dict, List, Optional, Sequence, Tuple, Union

from google.auth import credentials as auth_credentials
from google.protobuf import field_mask_pb2

from google.cloud.aiplatform import base
from google.cloud.aiplatform.compat.types import (
    entity_type as gca_entity_type,
    featurestore_service as gca_featurestore_service,
    io as gca_io,
)
from google.cloud.aiplatform import featurestore
from google.cloud.aiplatform import utils
from google.cloud.aiplatform.utils import featurestore_utils

_LOGGER = base.Logger(__name__)
_ALL_FEATURE_IDS = "*"


class EntityType(base.VertexAiResourceNounWithFutureManager):
    """Managed entityType resource for Vertex AI."""

    client_class = utils.FeaturestoreClientWithOverride

    _is_client_prediction_client = False
    _resource_noun = "entityTypes"
    _getter_method = "get_entity_type"
    _list_method = "list_entity_types"
    _delete_method = "delete_entity_type"
    _parse_resource_name_method = "parse_entity_type_path"
    _format_resource_name_method = "entity_type_path"

    @staticmethod
    def _resource_id_validator(resource_id: str):
        """Validates resource ID.

        Args:
            resource_id(str):
                The resource id to validate.
        """
        featurestore_utils.validate_id(resource_id)

    def __init__(
        self,
        entity_type_name: str,
        featurestore_id: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ):
        """Retrieves an existing managed entityType given an entityType resource name or an entity_type ID.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='projects/123/locations/us-central1/featurestores/my_featurestore_id/\
                entityTypes/my_entity_type_id'
            )
            or
            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )

        Args:
            entity_type_name (str):
                Required. A fully-qualified entityType resource name or an entity_type ID.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id/entityTypes/my_entity_type_id"
                or "my_entity_type_id" when project and location are initialized or passed, with featurestore_id passed.
            featurestore_id (str):
                Optional. Featurestore ID of an existing featurestore to retrieve entityType from,
                when entity_type_name is passed as entity_type ID.
            project (str):
                Optional. Project to retrieve entityType from. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to retrieve entityType from. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to retrieve this EntityType. Overrides
                credentials set in aiplatform.init.
        """

        super().__init__(
            project=project,
            location=location,
            credentials=credentials,
            resource_name=entity_type_name,
        )
        self._gca_resource = self._get_gca_resource(
            resource_name=entity_type_name,
            parent_resource_name_fields={
                featurestore.Featurestore._resource_noun: featurestore_id
            }
            if featurestore_id
            else featurestore_id,
        )

    @property
    def featurestore_name(self) -> str:
        """Full qualified resource name of the managed featurestore in which this EntityType is."""
        entity_type_name_components = self._parse_resource_name(self.resource_name)
        return featurestore.Featurestore._format_resource_name(
            project=entity_type_name_components["project"],
            location=entity_type_name_components["location"],
            featurestore=entity_type_name_components["featurestore"],
        )

    def get_featurestore(self) -> "featurestore.Featurestore":
        """Retrieves the managed featurestore in which this EntityType is.

        Returns:
            featurestore.Featurestore - The managed featurestore in which this EntityType is.
        """
        return featurestore.Featurestore(self.featurestore_name)

    def get_feature(self, feature_id: str) -> "featurestore.Feature":
        """Retrieves an existing managed feature in this EntityType.

        Args:
            feature_id (str):
                Required. The managed feature resource ID in this EntityType.
        Returns:
            featurestore.Feature - The managed feature resource object.
        """
        entity_type_name_components = self._parse_resource_name(self.resource_name)

        return featurestore.Feature(
            feature_name=featurestore.Feature._format_resource_name(
                project=entity_type_name_components["project"],
                location=entity_type_name_components["location"],
                featurestore=entity_type_name_components["featurestore"],
                entity_type=entity_type_name_components["entity_type"],
                feature=feature_id,
            )
        )

    def update(
        self,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "EntityType":
        """Updates an existing managed entityType resource.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_entity_type.update(
                description='update my description',
            )

        Args:
            description (str):
                Optional. Description of the EntityType.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your EntityTypes.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one Feature
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
        Returns:
            EntityType - The updated entityType resource object.
        """
        update_mask = list()

        if description:
            update_mask.append("description")

        if labels:
            utils.validate_labels(labels)
            update_mask.append("labels")

        update_mask = field_mask_pb2.FieldMask(paths=update_mask)

        gapic_entity_type = gca_entity_type.EntityType(
            name=self.resource_name, description=description, labels=labels,
        )

        _LOGGER.log_action_start_against_resource(
            "Updating", "entityType", self,
        )

        update_entity_type_lro = self.api_client.update_entity_type(
            entity_type=gapic_entity_type,
            update_mask=update_mask,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Update", "entityType", self.__class__, update_entity_type_lro
        )

        update_entity_type_lro.result()

        _LOGGER.log_action_completed_against_resource("entityType", "updated", self)

        return self

    @classmethod
    def list(
        cls,
        featurestore_name: str,
        filter: Optional[str] = None,
        order_by: Optional[str] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
    ) -> List["EntityType"]:
        """Lists existing managed entityType resources in a featurestore, given a featurestore resource name or a featurestore ID.

        Example Usage:

            my_entityTypes = aiplatform.EntityType.list(
                featurestore_name='projects/123/locations/us-central1/featurestores/my_featurestore_id'
            )
            or
            my_entityTypes = aiplatform.EntityType.list(
                featurestore_name='my_featurestore_id'
            )

        Args:
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID
                of an existing featurestore to list entityTypes in.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.
            filter (str):
                Optional. Lists the EntityTypes that match the filter expression. The
                following filters are supported:

                -  ``create_time``: Supports ``=``, ``!=``, ``<``, ``>``,
                   ``>=``, and ``<=`` comparisons. Values must be in RFC
                   3339 format.
                -  ``update_time``: Supports ``=``, ``!=``, ``<``, ``>``,
                   ``>=``, and ``<=`` comparisons. Values must be in RFC
                   3339 format.
                -  ``labels``: Supports key-value equality as well as key
                   presence.

                Examples:

                -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
                   --> EntityTypes created or updated after
                   2020-01-31T15:30:00.000000Z.
                -  ``labels.active = yes AND labels.env = prod`` -->
                   EntityTypes having both (active: yes) and (env: prod)
                   labels.
                -  ``labels.env: *`` --> Any EntityType which has a label
                   with 'env' as the key.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for
                descending.

                Supported fields:

                -  ``entity_type_id``
                -  ``create_time``
                -  ``update_time``
            project (str):
                Optional. Project to list entityTypes in. If not set, project
                set in aiplatform.init will be used.
            location (str):
                Optional. Location to list entityTypes in. If not set, location
                set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to list entityTypes. Overrides
                credentials set in aiplatform.init.

        Returns:
            List[EntityType] - A list of managed entityType resource objects
        """

        return cls._list(
            filter=filter,
            order_by=order_by,
            project=project,
            location=location,
            credentials=credentials,
            parent=utils.full_resource_name(
                resource_name=featurestore_name,
                resource_noun=featurestore.Featurestore._resource_noun,
                parse_resource_name_method=featurestore.Featurestore._parse_resource_name,
                format_resource_name_method=featurestore.Featurestore._format_resource_name,
                project=project,
                location=location,
                resource_id_validator=featurestore.Featurestore._resource_id_validator,
            ),
        )

    def list_features(
        self, filter: Optional[str] = None, order_by: Optional[str] = None,
    ) -> List["featurestore.Feature"]:
        """Lists existing managed feature resources in this EntityType.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_entityType.list_features()

        Args:
            filter (str):
                Optional. Lists the Features that match the filter expression. The
                following filters are supported:

                -  ``value_type``: Supports = and != comparisons.
                -  ``create_time``: Supports =, !=, <, >, >=, and <=
                   comparisons. Values must be in RFC 3339 format.
                -  ``update_time``: Supports =, !=, <, >, >=, and <=
                   comparisons. Values must be in RFC 3339 format.
                -  ``labels``: Supports key-value equality as well as key
                   presence.

                Examples:

                -  ``value_type = DOUBLE`` --> Features whose type is
                   DOUBLE.
                -  ``create_time > \"2020-01-31T15:30:00.000000Z\" OR update_time > \"2020-01-31T15:30:00.000000Z\"``
                   --> EntityTypes created or updated after
                   2020-01-31T15:30:00.000000Z.
                -  ``labels.active = yes AND labels.env = prod`` -->
                   Features having both (active: yes) and (env: prod)
                   labels.
                -  ``labels.env: *`` --> Any Feature which has a label with
                   'env' as the key.
            order_by (str):
                Optional. A comma-separated list of fields to order by, sorted in
                ascending order. Use "desc" after a field name for
                descending. Supported fields:

                -  ``feature_id``
                -  ``value_type``
                -  ``create_time``
                -  ``update_time``

        Returns:
            List[featurestore.Feature] - A list of managed feature resource objects.
        """
        return featurestore.Feature.list(
            entity_type_name=self.resource_name, filter=filter, order_by=order_by,
        )

    @base.optional_sync()
    def delete_features(self, feature_ids: List[str], sync: bool = True,) -> None:
        """Deletes feature resources in this EntityType given their feature IDs.
        WARNING: This deletion is permanent.

        Args:
            feature_ids (List[str]):
                Required. The list of feature IDs to be deleted.
            sync (bool):
                Optional. Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        """
        features = []
        for feature_id in feature_ids:
            feature = self.get_feature(feature_id=feature_id)
            feature.delete(sync=False)
            features.append(feature)

        for feature in features:
            feature.wait()

    @base.optional_sync()
    def delete(self, sync: bool = True, force: bool = False) -> None:
        """Deletes this EntityType resource. If force is set to True,
        all features in this EntityType will be deleted prior to entityType deletion.

        WARNING: This deletion is permanent.

        Args:
            force (bool):
                If set to true, any Features for this
                EntityType will also be deleted.
                (Otherwise, the request will only work
                if the EntityType has no Features.)
            sync (bool):
                Whether to execute this deletion synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.
        Raises:
            FailedPrecondition: If features are created in this EntityType and force = False.
        """
        _LOGGER.log_action_start_against_resource("Deleting", "", self)
        lro = getattr(self.api_client, self._delete_method)(
            name=self.resource_name, force=force
        )
        _LOGGER.log_action_started_against_resource_with_lro(
            "Delete", "", self.__class__, lro
        )
        lro.result()
        _LOGGER.log_action_completed_against_resource("deleted.", "", self)

    @classmethod
    @base.optional_sync()
    def create(
        cls,
        entity_type_id: str,
        featurestore_name: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        project: Optional[str] = None,
        location: Optional[str] = None,
        credentials: Optional[auth_credentials.Credentials] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "EntityType":
        """Creates an EntityType resource in a Featurestore.

        Example Usage:

            my_entity_type = aiplatform.EntityType.create(
                entity_type_id='my_entity_type_id',
                featurestore_name='projects/123/locations/us-central1/featurestores/my_featurestore_id'
            )
            or
            my_entity_type = aiplatform.EntityType.create(
                entity_type_id='my_entity_type_id',
                featurestore_name='my_featurestore_id',
            )

        Args:
            entity_type_id (str):
                Required. The ID to use for the EntityType, which will
                become the final component of the EntityType's resource
                name.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within a featurestore.
            featurestore_name (str):
                Required. A fully-qualified featurestore resource name or a featurestore ID
                of an existing featurestore to create EntityType in.
                Example: "projects/123/locations/us-central1/featurestores/my_featurestore_id"
                or "my_featurestore_id" when project and location are initialized or passed.
            description (str):
                Optional. Description of the EntityType.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your EntityTypes.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one EntityType
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            project (str):
                Optional. Project to create EntityType in if `featurestore_name` is passed an featurestore ID.
                If not set, project set in aiplatform.init will be used.
            location (str):
                Optional. Location to create EntityType in if `featurestore_name` is passed an featurestore ID.
                If not set, location set in aiplatform.init will be used.
            credentials (auth_credentials.Credentials):
                Optional. Custom credentials to use to create EntityTypes. Overrides
                credentials set in aiplatform.init.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            EntityType - entity_type resource object

        """

        featurestore_name = utils.full_resource_name(
            resource_name=featurestore_name,
            resource_noun=featurestore.Featurestore._resource_noun,
            parse_resource_name_method=featurestore.Featurestore._parse_resource_name,
            format_resource_name_method=featurestore.Featurestore._format_resource_name,
            project=project,
            location=location,
            resource_id_validator=featurestore.Featurestore._resource_id_validator,
        )

        featurestore_name_components = featurestore.Featurestore._parse_resource_name(
            featurestore_name
        )

        gapic_entity_type = gca_entity_type.EntityType()

        if labels:
            utils.validate_labels(labels)
            gapic_entity_type.labels = labels

        if description:
            gapic_entity_type.description = description

        api_client = cls._instantiate_client(
            location=featurestore_name_components["location"], credentials=credentials,
        )

        created_entity_type_lro = api_client.create_entity_type(
            parent=featurestore_name,
            entity_type=gapic_entity_type,
            entity_type_id=entity_type_id,
            metadata=request_metadata,
        )

        _LOGGER.log_create_with_lro(cls, created_entity_type_lro)

        created_entity_type = created_entity_type_lro.result()

        _LOGGER.log_create_complete(cls, created_entity_type, "entity_type")

        entity_type_obj = cls(
            entity_type_name=created_entity_type.name,
            project=project,
            location=location,
            credentials=credentials,
        )

        return entity_type_obj

    def create_feature(
        self,
        feature_id: str,
        value_type: str,
        description: Optional[str] = None,
        labels: Optional[Dict[str, str]] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "featurestore.Feature":
        """Creates a Feature resource in this EntityType.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_feature = my_entity_type.create_feature(
                feature_id='my_feature_id',
                value_type='INT64',
            )

        Args:
            feature_id (str):
                Required. The ID to use for the Feature, which will become
                the final component of the Feature's resource name, which is immutable.

                This value may be up to 60 characters, and valid characters
                are ``[a-z0-9_]``. The first character cannot be a number.

                The value must be unique within an EntityType.
            value_type (str):
                Required. Immutable. Type of Feature value.
                One of BOOL, BOOL_ARRAY, DOUBLE, DOUBLE_ARRAY, INT64, INT64_ARRAY, STRING, STRING_ARRAY, BYTES.
            description (str):
                Optional. Description of the Feature.
            labels (Dict[str, str]):
                Optional. The labels with user-defined
                metadata to organize your Features.
                Label keys and values can be no longer than 64
                characters (Unicode codepoints), can only
                contain lowercase letters, numeric characters,
                underscores and dashes. International characters
                are allowed.
                See https://goo.gl/xmQnxf for more information
                on and examples of labels. No more than 64 user
                labels can be associated with one Feature
                (System labels are excluded)."
                System reserved label keys are prefixed with
                "aiplatform.googleapis.com/" and are immutable.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            featurestore.Feature - feature resource object

        """
        return featurestore.Feature.create(
            feature_id=feature_id,
            value_type=value_type,
            entity_type_name=self.resource_name,
            description=description,
            labels=labels,
            request_metadata=request_metadata,
            sync=sync,
        )

    def _validate_and_get_create_feature_requests(
        self,
        feature_configs: Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]],
    ) -> List[gca_featurestore_service.CreateFeatureRequest]:
        """ Validates feature_configs and get requests for batch feature creation

        Args:
            feature_configs (Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]]):
                Required. A user defined Dict containing configurations for feature creation.

        Returns:
            List[gca_featurestore_service.CreateFeatureRequest] - requests for batch feature creation
        """

        requests = []
        for feature_id, feature_config in feature_configs.items():
            feature_config = featurestore_utils._FeatureConfig(
                feature_id=feature_id,
                value_type=feature_config.get(
                    "value_type", featurestore_utils._FEATURE_VALUE_TYPE_UNSPECIFIED
                ),
                description=feature_config.get("description", None),
                labels=feature_config.get("labels", {}),
            )
            create_feature_request = feature_config.get_create_feature_request()
            requests.append(create_feature_request)

        return requests

    @base.optional_sync(return_input_arg="self")
    def batch_create_features(
        self,
        feature_configs: Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]],
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "EntityType":
        """Batch creates Feature resources in this EntityType.

        Example Usage:

            my_entity_type = aiplatform.EntityType(
                entity_type_name='my_entity_type_id',
                featurestore_id='my_featurestore_id',
            )
            my_entity_type.batch_create_features(
                feature_configs={
                    "my_feature_id1": {
                            "value_type": "INT64",
                        },
                    "my_feature_id2": {
                            "value_type": "BOOL",
                        },
                    "my_feature_id3": {
                            "value_type": "STRING",
                        },
                }
            )

        Args:
            feature_configs (Dict[str, Dict[str, Union[bool, int, Dict[str, str], str]]]):
                Required. A user defined Dict containing configurations for feature creation.

                The feature_configs Dict[str, Dict] i.e. {feature_id: feature_config} contains configuration for each creating feature:
                Example:
                    feature_configs = {
                        "my_feature_id_1": feature_config_1,
                        "my_feature_id_2": feature_config_2,
                        "my_feature_id_3": feature_config_3,
                    }

                Each feature_config requires "value_type", and optional "description", "labels":
                Example:
                    feature_config_1 = {
                        "value_type": "INT64",
                    }
                    feature_config_2 = {
                        "value_type": "BOOL",
                        "description": "my feature id 2 description"
                    }
                    feature_config_3 = {
                        "value_type": "STRING",
                        "labels": {
                            "my key": "my value",
                        }
                    }

            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this creation synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            EntityType - entity_type resource object
        """
        create_feature_requests = self._validate_and_get_create_feature_requests(
            feature_configs=feature_configs
        )

        _LOGGER.log_action_start_against_resource(
            "Batch creating features", "entityType", self,
        )

        batch_created_features_lro = self.api_client.batch_create_features(
            parent=self.resource_name,
            requests=create_feature_requests,
            metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Batch create Features",
            "entityType",
            self.__class__,
            batch_created_features_lro,
        )

        batch_created_features_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "entityType", "Batch created features", self
        )

        return self

    def _validate_and_get_import_feature_values_request(
        self,
        feature_ids: List[str],
        feature_time: Union[str, datetime.datetime],
        data_source: Union[gca_io.AvroSource, gca_io.BigQuerySource, gca_io.CsvSource],
        feature_source_fields: Optional[Dict[str, str]] = None,
        entity_id_field: Optional[str] = None,
        disable_online_serving: Optional[bool] = None,
        worker_count: Optional[int] = None,
    ) -> gca_featurestore_service.ImportFeatureValuesRequest:
        """Validates and get import feature values request.
        Args:
            feature_ids (List[str]):
                Required. IDs of the Feature to import values
                of. The Features must exist in the target
                EntityType, or the request will fail.
            feature_time (Union[str, datetime.datetime]):
                Required. The feature_time can be one of:
                    - The source column that holds the Feature
                    timestamp for all Feature values in each entity.
                    - A single Feature timestamp for all entities
                    being imported. The timestamp must not have
                    higher than millisecond precision.
            data_source (Union[gca_io.AvroSource, gca_io.BiqQuerySource, gca_io.CsvSource]):
                Required. The data_source can be one of:
                    - AvroSource
                    - BiqQuerySource
                    - CsvSource
            feature_source_fields (Dict[str, str]):
                Optional. User defined dictionary to map ID of the Feature for importing values
                of to the source column for getting the Feature values from.

                Specify the features whose ID and source column are not the same.
                If not provided, the source column need to be the same as the Feature ID.

                Example:

                     feature_ids = ['my_feature_id_1', 'my_feature_id_2', 'my_feature_id_3']

                     In case all features' source field and ID match:
                     feature_source_fields = None or {}

                     In case all features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                        'my_feature_id_2': 'my_feature_id_2_source_field',
                        'my_feature_id_3': 'my_feature_id_3_source_field',
                     }

                     In case some features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                     }
            entity_id_field (str):
                Optional. Source column that holds entity IDs. If not provided, entity
                IDs are extracted from the column named ``entity_id``.
            disable_online_serving (bool):
                Optional. If set, data will not be imported for online
                serving. This is typically used for backfilling,
                where Feature generation timestamps are not in
                the timestamp range needed for online serving.
            worker_count (int):
                Optional. Specifies the number of workers that are used
                to write data to the Featurestore. Consider the
                online serving capacity that you require to
                achieve the desired import throughput without
                interfering with online serving. The value must
                be positive, and less than or equal to 100. If
                not set, defaults to using 1 worker. The low
                count ensures minimal impact on online serving
                performance.
        Returns:
            gca_featurestore_service.ImportFeatureValuesRequest - request message for importing feature values
        Raises:
            ValueError if data_source type is not supported
            ValueError if feature_time type is not supported
        """
        feature_source_fields = feature_source_fields or {}
        feature_specs = [
            gca_featurestore_service.ImportFeatureValuesRequest.FeatureSpec(
                id=feature_id, source_field=feature_source_fields.get(feature_id)
            )
            for feature_id in set(feature_ids)
        ]

        import_feature_values_request = gca_featurestore_service.ImportFeatureValuesRequest(
            entity_type=self.resource_name,
            feature_specs=feature_specs,
            entity_id_field=entity_id_field,
            disable_online_serving=disable_online_serving,
            worker_count=worker_count,
        )

        if isinstance(data_source, gca_io.AvroSource):
            import_feature_values_request.avro_source = data_source
        elif isinstance(data_source, gca_io.BigQuerySource):
            import_feature_values_request.bigquery_source = data_source
        elif isinstance(data_source, gca_io.CsvSource):
            import_feature_values_request.csv_source = data_source
        else:
            raise ValueError(
                f"The type of `data_source` field should be: "
                f"`gca_io.AvroSource`, `gca_io.BigQuerySource`, or `gca_io.CsvSource`, "
                f"get {type(data_source)} instead. "
            )

        if isinstance(feature_time, str):
            import_feature_values_request.feature_time_field = feature_time
        elif isinstance(feature_time, datetime.datetime):
            import_feature_values_request.feature_time = utils.get_timestamp_proto(
                time=feature_time
            )
        else:
            raise ValueError(
                f"The type of `feature_time` field should be: `str` or `datetime.datetime`, "
                f"get {type(feature_time)} instead. "
            )

        return import_feature_values_request

    def _import_feature_values(
        self,
        import_feature_values_request: gca_featurestore_service.ImportFeatureValuesRequest,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
    ) -> "EntityType":
        """Imports Feature values into the Featurestore from a source storage.

        Args:
            import_feature_values_request (gca_featurestore_service.ImportFeatureValuesRequest):
                Required. Request message for importing feature values.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.

        Returns:
            EntityType - The entityType resource object with imported feature values.
        """
        _LOGGER.log_action_start_against_resource(
            "Importing", "feature values", self,
        )

        import_lro = self.api_client.import_feature_values(
            request=import_feature_values_request, metadata=request_metadata,
        )

        _LOGGER.log_action_started_against_resource_with_lro(
            "Import", "feature values", self.__class__, import_lro
        )

        import_lro.result()

        _LOGGER.log_action_completed_against_resource(
            "feature values", "imported", self
        )

        return self

    @base.optional_sync(return_input_arg="self")
    def ingest_from_bq(
        self,
        feature_ids: List[str],
        feature_time: Union[str, datetime.datetime],
        bq_source_uri: str,
        feature_source_fields: Optional[Dict[str, str]] = None,
        entity_id_field: Optional[str] = None,
        disable_online_serving: Optional[bool] = None,
        worker_count: Optional[int] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "EntityType":
        """Ingest feature values from BigQuery.

        Args:
            feature_ids (List[str]):
                Required. IDs of the Feature to import values
                of. The Features must exist in the target
                EntityType, or the request will fail.
            feature_time (Union[str, datetime.datetime]):
                Required. The feature_time can be one of:
                    - The source column that holds the Feature
                    timestamp for all Feature values in each entity.
                    - A single Feature timestamp for all entities
                    being imported. The timestamp must not have
                    higher than millisecond precision.
            bq_source_uri (str):
                Required. BigQuery URI to the input table.
                Example:
                    'bq://project.dataset.table_name'
            feature_source_fields (Dict[str, str]):
                Optional. User defined dictionary to map ID of the Feature for importing values
                of to the source column for getting the Feature values from.

                Specify the features whose ID and source column are not the same.
                If not provided, the source column need to be the same as the Feature ID.

                Example:

                     feature_ids = ['my_feature_id_1', 'my_feature_id_2', 'my_feature_id_3']

                     In case all features' source field and ID match:
                     feature_source_fields = None or {}

                     In case all features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                        'my_feature_id_2': 'my_feature_id_2_source_field',
                        'my_feature_id_3': 'my_feature_id_3_source_field',
                     }

                     In case some features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                     }
            entity_id_field (str):
                Optional. Source column that holds entity IDs. If not provided, entity
                IDs are extracted from the column named ``entity_id``.
            disable_online_serving (bool):
                Optional. If set, data will not be imported for online
                serving. This is typically used for backfilling,
                where Feature generation timestamps are not in
                the timestamp range needed for online serving.
            worker_count (int):
                Optional. Specifies the number of workers that are used
                to write data to the Featurestore. Consider the
                online serving capacity that you require to
                achieve the desired import throughput without
                interfering with online serving. The value must
                be positive, and less than or equal to 100. If
                not set, defaults to using 1 worker. The low
                count ensures minimal impact on online serving
                performance.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this import synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            EntityType - The entityType resource object with feature values imported.

        """
        bigquery_source = gca_io.BigQuerySource(input_uri=bq_source_uri)

        import_feature_values_request = self._validate_and_get_import_feature_values_request(
            feature_ids=feature_ids,
            feature_time=feature_time,
            data_source=bigquery_source,
            feature_source_fields=feature_source_fields,
            entity_id_field=entity_id_field,
            disable_online_serving=disable_online_serving,
            worker_count=worker_count,
        )

        return self._import_feature_values(
            import_feature_values_request=import_feature_values_request,
            request_metadata=request_metadata,
        )

    @base.optional_sync(return_input_arg="self")
    def ingest_from_gcs(
        self,
        feature_ids: List[str],
        feature_time: Union[str, datetime.datetime],
        gcs_source_uris: Union[str, List[str]],
        gcs_source_type: str,
        feature_source_fields: Optional[Dict[str, str]] = None,
        entity_id_field: Optional[str] = None,
        disable_online_serving: Optional[bool] = None,
        worker_count: Optional[int] = None,
        request_metadata: Optional[Sequence[Tuple[str, str]]] = (),
        sync: bool = True,
    ) -> "EntityType":
        """Ingest feature values from GCS.

        Args:
            feature_ids (List[str]):
                Required. IDs of the Feature to import values
                of. The Features must exist in the target
                EntityType, or the request will fail.
            feature_time (Union[str, datetime.datetime]):
                Required. The feature_time can be one of:
                    - The source column that holds the Feature
                    timestamp for all Feature values in each entity.
                    - A single Feature timestamp for all entities
                    being imported. The timestamp must not have
                    higher than millisecond precision.
            gcs_source_uris (Union[str, List[str]]):
                Required. Google Cloud Storage URI(-s) to the
                input file(s). May contain wildcards. For more
                information on wildcards, see
                https://cloud.google.com/storage/docs/gsutil/addlhelp/WildcardNames.
                Example:
                    ["gs://my_bucket/my_file_1.csv", "gs://my_bucket/my_file_2.csv"]
                    or
                    "gs://my_bucket/my_file.avro"
            gcs_source_type (str):
                Required. The type of the input file(s) provided by `gcs_source_uris`,
                the value of gcs_source_type can only be either `csv`, or `avro`.
            feature_source_fields (Dict[str, str]):
                Optional. User defined dictionary to map ID of the Feature for importing values
                of to the source column for getting the Feature values from.

                Specify the features whose ID and source column are not the same.
                If not provided, the source column need to be the same as the Feature ID.

                Example:

                     feature_ids = ['my_feature_id_1', 'my_feature_id_2', 'my_feature_id_3']

                     In case all features' source field and ID match:
                     feature_source_fields = None or {}

                     In case all features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                        'my_feature_id_2': 'my_feature_id_2_source_field',
                        'my_feature_id_3': 'my_feature_id_3_source_field',
                     }

                     In case some features' source field and ID do not match:
                     feature_source_fields = {
                        'my_feature_id_1': 'my_feature_id_1_source_field',
                     }
            entity_id_field (str):
                Optional. Source column that holds entity IDs. If not provided, entity
                IDs are extracted from the column named ``entity_id``.
            disable_online_serving (bool):
                Optional. If set, data will not be imported for online
                serving. This is typically used for backfilling,
                where Feature generation timestamps are not in
                the timestamp range needed for online serving.
            worker_count (int):
                Optional. Specifies the number of workers that are used
                to write data to the Featurestore. Consider the
                online serving capacity that you require to
                achieve the desired import throughput without
                interfering with online serving. The value must
                be positive, and less than or equal to 100. If
                not set, defaults to using 1 worker. The low
                count ensures minimal impact on online serving
                performance.
            request_metadata (Sequence[Tuple[str, str]]):
                Optional. Strings which should be sent along with the request as metadata.
            sync (bool):
                Optional. Whether to execute this import synchronously. If False, this method
                will be executed in concurrent Future and any downstream object will
                be immediately returned and synced when the Future has completed.

        Returns:
            EntityType - The entityType resource object with feature values imported.

        Raises:
            ValueError if gcs_source_type is not supported.
        """
        if gcs_source_type not in featurestore_utils.GCS_SOURCE_TYPE:
            raise ValueError(
                "Only %s are supported gcs_source_type, not `%s`. "
                % (
                    "`" + "`, `".join(featurestore_utils.GCS_SOURCE_TYPE) + "`",
                    gcs_source_type,
                )
            )

        if isinstance(gcs_source_uris, str):
            gcs_source_uris = [gcs_source_uris]
        gcs_source = gca_io.GcsSource(uris=gcs_source_uris)

        if gcs_source_type == "csv":
            data_source = gca_io.CsvSource(gcs_source=gcs_source)
        if gcs_source_type == "avro":
            data_source = gca_io.AvroSource(gcs_source=gcs_source)

        import_feature_values_request = self._validate_and_get_import_feature_values_request(
            feature_ids=feature_ids,
            feature_time=feature_time,
            data_source=data_source,
            feature_source_fields=feature_source_fields,
            entity_id_field=entity_id_field,
            disable_online_serving=disable_online_serving,
            worker_count=worker_count,
        )

        return self._import_feature_values(
            import_feature_values_request=import_feature_values_request,
            request_metadata=request_metadata,
        )