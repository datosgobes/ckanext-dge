# Copyright (C) 2025 Entidad Pública Empresarial Red.es
#
# This file is part of "dge (datos.gob.es)".
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

# dataset include fields
DATASET_INCLUDE_FIELDS = {
    'issued_date': 'issued_date',
    'modified_date': 'modified_date',
    'frequency': 'frequency',
    'coverage_new': 'coverage_new',
    'spatial': 'spatial',
    'spatial_detail': 'spatial_detail',
    'language': 'language',
    'valid': 'valid',
    'conforms_to': 'conforms_to',
    'reference': 'reference',
    'rate': 'rate',
    'rate_info': 'rate_info',
    'identifier': 'identifier',
    'was_generated_by': 'was_generated_by',
    'is_referenced_by': 'is_referenced_by',
    'landing_page': 'landing_page',
    'is_version_of': 'is_version_of',
    'another_identifier': 'another_identifier',
    'source': 'source',
    'has_version': 'has_version',
    'relation': 'relation',
    'provenance': 'provenance',
    'page': 'page',
    'dataset_type': 'dataset_type',
    'dataset_version': 'dataset_version',
    'version_notes': 'version_notes',
    'spatial_resolution_in_meters': 'spatial_resolution_in_meters',
    'temporal_resolution': 'temporal_resolution',
    'access_rights': 'access_rights',
    'qualified_attribution': 'qualified_attribution',
    'qualified_relation': 'qualified_relation',
    'creator': 'creator',
    'contact_point': 'contact_point',
    'hvd_applicable_legislation': 'hvd_applicable_legislation',
    'hvd_category': 'hvd_category',
    'multilingual_tags': 'multilingual_tags',
    'license_id': 'license_id',
    'description': 'description',
    'served_by_dataservice': 'served_by_dataservice',
    'theme': 'theme'
}

DATASET_INFORMATION_INFO_FIELDS = [
    'hvd_category',
    'multilingual_tags',
    'spatial',
    'coverage_new',
    'frequency',
    'language',
    'dataset_type',
    'theme'
]

DATASET_TECHNICAL_SHEET_INFO_FIELDS = [
    'identifier',
    'another_identifier',
    'modified_date',
    'issued_date',
    'spatial_resolution_in_meters',
    'temporal_resolution',
    'relation',
    'source',
    'is_referenced_by',
    'qualified_relation',
    'dataset_version',
    'version_notes',
    'has_version',
    'is_version_of'
]

DATASET_CONTACT_INFO_FIELDS = [
    'contact_point',
    'creator'
]

DATASET_QUALITY_INFO_FIELDS = [
    'hvd_applicable_legislation',
    'conforms_to',
    'access_rights',
    'page',
    'landing_page',
    'provenance',
    'was_generated_by',
    'qualified_attribution'
]

RESOURCE_INCLUDE_FIELDS = {
    'access_url': 'access_url',
    'resource_hvd_applicable_legislation': 'resource_hvd_applicable_legislation',
    'resource_description': 'resource_description',
    'availability': 'availability',
    'resource_license': 'resource_license',
    'access_service': 'access_service',
    'resource_page': 'resource_page',
    'media_type': 'media_type',
    'resource_format': 'resource_format',
    'download_url': 'download_url',
    'resource_conforms_to': 'resource_conforms_to',
    'resource_issued_date': 'resource_issued_date',
    'resource_modified_date': 'resource_modified_date',
    'resource_status': 'resource_status',
    'resource_language': 'resource_language',
    'compress_format': 'compress_format',
    'package_format': 'package_format',
    'resource_spatial_resolution_in_meters': 'resource_spatial_resolution_in_meters',
    'resource_temporal_resolution': 'resource_temporal_resolution',
    'checksum': 'checksum',
    'has_policy': 'has_policy',
    'resource_rights': 'resource_rights',
    'byte_size': 'byte_size',
    'format': 'format',
    'resource_identifier': 'resource_identifier',
    'resource_relation': 'resource_relation'
}

RESOURCE_IDENTIFICATION_INFO_FIELDS = [
    'resource_description',
    'access_url',
    'download_url',
    'resource_language',
    'resource_modified_date',
    'resource_issued_date',
    'checksum'
]

RESOURCE_INTEROPERABILITY_INFO_FIELDS = [
    'resource_format',
    'format',
    'access_service',
    'package_format',
    'compress_format',
    'byte_size'
]

RESOURCE_PROVENANCE_INFO_FIELDS = [
    'resource_hvd_applicable_legislation',
    'resource_spatial_resolution_in_meters',
    'resource_temporal_resolution',
    'has_policy',
    'resource_conforms_to'
]

RESOURCE_REUSABILITY_INFO_FIELDS = [
    'resource_page',
    'resource_rights',
    'resource_status',
    'availability'
]


DATASERVICE_INCLUDE_FIELDS = {
    'title_translated': 'title_translated',
    'description': 'description',
    'hvd_applicable_legislation': 'hvd_applicable_legislation',
    'hvd_category': 'hvd_category',
    'contact_point': 'contact_point',
    'page': 'page',
    'endpoint_url': 'endpoint_url',
    'endpoint_description': 'endpoint_description',
    'access_rights': 'access_rights',
    'license_id': 'license_id',
    'multilingual_tags': 'multilingual_tags',
    'theme': 'theme'
}

DATASERVICE_INFORMATION_INFO_FIELDS = [
    'hvd_category',
    'multilingual_tags',
    'endpoint_url',
    'endpoint_description',
    'page',
    'theme'
]

DATASERVICE_CONTACT_INFO_FIELDS = [
    'contact_point'
]

DATASERVICE_QUALITY_INFO_FIELDS = [
    'hvd_applicable_legislation',
    'access_rights',
    'license_id'
]


EUROPEAN_PREFIX = 'http://publications.europa.eu/resource/authority/'
INSPIRE_PREFIX = 'http://inspire.ec.europa.eu/'
IANA_PREFIX = 'http://www.iana.org/assignments/'
SPATIAL_GEONAMES_PREFIX = 'http://sws.geonames.org/'
SPATIAL_GEONAMES_HTTPS_PREFIX = 'https://sws.geonames.org/'
SPATIAL_DATOSGOBES_PREFIX = 'http://datos.gob.es/recurso/sector-publico/territorio/'
DGE_IANA_FORMATS_PREFIX_HTTP = 'http://www.iana.org/assignments/media-types/'
DGE_IANA_FORMATS_PREFIX_HTTPS = 'https://www.iana.org/assignments/media-types/'
DGE_IANA_FORMATS_PREFIXES = ('http://www.iana.org/assignments/media-types/', 'https://www.iana.org/assignments/media-types/')
THEME_DATOSGOBES_PREFIX = 'http://datos.gob.es/kos/sector-publico/sector/'
THEME_INSPIRE_PREFIX = 'http://inspire.ec.europa.eu/theme/'
DATASET_TYPE_INSPIRE_PREFIX = 'http://inspire.ec.europa.eu/metadata-codelist/ResourceType/'
HTTPS_PREFIX = 'https'
HTTP_PREFIX = 'http'

VOCABULARY_PREFIX_TUPLE = (
    EUROPEAN_PREFIX,
    INSPIRE_PREFIX,
    SPATIAL_GEONAMES_PREFIX,
    SPATIAL_GEONAMES_HTTPS_PREFIX
)

DGE_HARVEST_UPDATE_FREQUENCIES = ['MANUAL','MONTHLY','WEEKLY','BIWEEKLY']
VALUE_APPLICATION_PROFILE_DCATAPES = 'dcatapes_100'
KEY_EXTRA_DATASET_APPLICATION_PROFILE = 'application_profile'
KEY_EXTRA_DATASET_SERVED_BY_DATASERVICE = 'served_by_dataservice'
KEY_EXTRA_DATASET_GUID = 'guid'
KEY_EXTRA_DATASET_HVD = 'hvd'

UNDEFINED_FORMAT_LABEL = 'undefined'

REQUEST_PARAM_DATASERVICE = '+dataset_type:dataservice'