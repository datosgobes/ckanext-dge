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

#!/usr/bin/env python
# -*- coding: 850 -*-
# -*- coding: utf-8 -*-
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import ckan.lib.helpers as h
import ckanext.scheming.helpers as sh
import ckanext.dge_scheming.helpers as dsh
import ckanext.dge_scheming.constants as ds_constants
import ckan.model as model
from  ckan.lib.base import abort
from ckan.plugins.toolkit import config
from ckanext.dge import helpers
from ckanext.dge.helpers import TRANSLATED_UNITS as TRANSLATED_UNITS
from ckanext.dge.helpers import DEFAULT_UNIT as DEFAULT_UNIT
from ckanext.dge.helpers import FACET_OPERATOR_PARAM_NAME as FACET_OPERATOR_PARAM_NAME
from ckanext.dge.helpers import FACET_SORT_PARAM_NAME as FACET_SORT_PARAM_NAME
import ckanext.dge.constants as dc
from collections import OrderedDict
from routes.mapper import SubMapper
from ckan.lib.plugins import DefaultTranslation
import ckan.logic as logic
import ckan.logic.auth as logic_auth
import ckan.logic.action as logic_action
import ckan.authz as authz
from ckan.common import (_, request, c)
import ckan.lib.base as base
import ckan.lib.plugins as lib_plugins
import ckan.lib.dictization.model_dictize as model_dictize
import json
import logging
import sys
import ckan.plugins as p
import ckanext.dge.views.dgeFeed as dge_feed_bl
import ckanext.dge.views.dgeOrganization as dge_org_bl
import ckanext.dge.views.dgePackage as dge_package_bl
import ckanext.dge.views.dgeDataservice as dge_dataservice_bl
import ckanext.dge.views.dgeUtil as dge_util_bl
import ckanext.dge.views.dge as dge_bl
import ckanext.dge.views.error as error_bl
import ckanext.dge.views.util as util_bl
import ckanext.dge.views.package as package_bl
import re

log = logging.getLogger(__name__)
is_frontend = False


@toolkit.auth_allow_anonymous_access
def dge_organization_publisher(context, data_dict=None):
    try:
        model = context['model']
        id = logic.get_or_bust(data_dict, 'id')
        group = model.Group.get(id)
        context['group'] = group
        if group is None:
            raise NotFound
        if not group.is_organization:
            raise NotFound
        group_dict = model_dictize.group_dictize(group, context,
                                                 packages_field='dataset_count',
                                                 include_tags=False,
                                                 include_extras=True,
                                                 include_groups=False,
                                                 include_users=False,)
        group_plugin = lib_plugins.lookup_group_plugin(group_dict['type'])
        schema = logic.schema.default_show_group_schema()
        group_dict, errors = lib_plugins.plugin_validate(
            group_plugin, context, group_dict, schema,
            'organization_show')
        return group_dict
    except:
        return {}

def dge_organization_show(context, data_dict=None):
    authorized = True
    user = context['user']
    group = logic_auth.get_group_object(context, data_dict)
    if group:
        orgs = toolkit.get_action('organization_list_for_user')(data_dict={'permission': 'read'})
        if orgs:
             org_ids = [org_tuple['id'] for org_tuple in orgs]
             authorized = True if group.id in org_ids else False
    if not authorized:
        return {'success': False,
             'msg': _('User %s not authorized to edit organization %s') %
                         (user, group.id)}
    else:
        return {'success': True}

def dge_harvest_source_show(context, data_dict=None):
    authorized = False
    user = context['user']
    package_id = data_dict['id']
    owner_org = data_dict['owner_org']
    orgs = toolkit.get_action('organization_list_for_user')(data_dict={'permission': 'read'})
    if orgs:
        org_ids = [org_tuple['id'] for org_tuple in orgs]
        authorized = True if owner_org in org_ids else False
    if not authorized:
        return {'success': False,
                 'msg': _('User %s not authorized to show harvest source %s') %
                             (user, package_id)}
    else:
        return {'success': True}



class DgePlugin(plugins.SingletonPlugin, DefaultTranslation):
    plugins.implements(plugins.IPackageController, inherit=True)
    plugins.implements(plugins.IResourceController, inherit=True)
    plugins.implements(plugins.ITemplateHelpers, inherit=True)

    if helpers.dge_is_frontend():
        log.debug('IS_FRONTEND')
        plugins.implements(plugins.ITranslation, inherit=True)
        plugins.implements(plugins.IConfigurer, inherit=True)
        plugins.implements(plugins.IAuthFunctions, inherit=True)
        plugins.implements(plugins.IFacets, inherit=True)
        plugins.implements(plugins.IBlueprint, inherit=True)
        plugins.implements(plugins.IActions, inherit=True)

    def get_blueprint(self):
        return [dge_bl.dge,
                dge_util_bl.dgeUtil,
                dge_feed_bl.dgeFeed,
                dge_org_bl.dgeOrganization,
                dge_package_bl.dgePackage,
                dge_dataservice_bl.dge_dataservice_bp,
                error_bl.error,
                package_bl.package,
                util_bl.util_bl]


    def get_actions(self):
        if not helpers.dge_is_frontend():
            return {}
        return {'dge_organization_publisher' : dge_organization_publisher,}


    def get_auth_functions(self):
        if not helpers.dge_is_frontend():
            return {}

        unauthorized = lambda context, data_dict: {'success': False}
        authorized = lambda context, data_dict: {'success': True}
        return {
            'organization_show': dge_organization_show,
            'dge_harvest_source_show': dge_harvest_source_show,
            'dge_organization_publisher': authorized,
            }


    def update_config(self, config_):
        if helpers.dge_is_frontend():
            toolkit.add_template_directory(config_, 'templates')
            toolkit.add_public_directory(config_, 'public')
            toolkit.add_resource('assets', 'dge')


    def _facets(self, facets_dict):
        if helpers.dge_is_frontend():
            if 'group' in facets_dict:
                del facets_dict['group']
        return facets_dict

    def dataset_facets(self, facets_dict, package_type):
        if not helpers.dge_is_frontend():
            return facets_dict
        lang_code = toolkit.request.environ['CKAN_LANG']
        facets_dict.clear()
        facets_dict['is_hvd'] = plugins.toolkit._('High-Value Dataset')
        facets_dict['theme_id'] = plugins.toolkit._('Category')
        facets_dict['res_format_label'] = plugins.toolkit._('Format')
        facets_dict['publisher_display_name'] = plugins.toolkit._('Publisher')
        facets_dict['administration_level'] = plugins.toolkit._('Administration level')
        facets_dict['frequency_label'] = plugins.toolkit._('Update frequency')
        tag_key = 'tags_' + lang_code
        facets_dict[tag_key] = plugins.toolkit._('Tag')

        return self._facets(facets_dict)

    def group_facets(self, facets_dict, group_type, package_type):
        if not helpers.dge_is_frontend():
            return facets_dict
        elif group_type == "organization":
            return self.organization_facets(facets_dict, group_type, package_type)
        
        return self._facets(facets_dict)

    def organization_facets(self, facets_dict, organization_type, package_type):
        if not helpers.dge_is_frontend():
            return facets_dict

        lang_code = toolkit.request.environ['CKAN_LANG']
        facets_dict.clear()

        facets_dict['organization'] = plugins.toolkit._('Organization')
        facets_dict['theme_id'] =  plugins.toolkit._('Category')
        facets_dict['res_format_label'] = plugins.toolkit._('Format')
        facets_dict['publisher_display_name'] = plugins.toolkit._('Publisher')
        facets_dict['administration_level'] = plugins.toolkit._('Administration level')
        facets_dict['frequency'] = plugins.toolkit._('Update frequency')
        tag_key = 'tags_' + lang_code
        facets_dict[tag_key] = plugins.toolkit._('Tag')

        return self._facets(facets_dict)


    def get_helpers(self):
        return {
            'dge_default_locale': helpers.dge_default_locale,
            'dge_dataset_field_value': helpers.dge_dataset_field_value,
            'dge_dataset_display_fields': helpers.dge_dataset_display_fields,
            'dge_dataset_tag_field_value': helpers.dge_dataset_tag_field_value,
            'dge_render_datetime': helpers.dge_render_datetime,
            'dge_parse_datetime': helpers.dge_parse_datetime,
            'dge_is_downloadable_resource': helpers.dge_is_downloadable_resource,
            'dge_dataset_display_name': helpers.dge_dataset_display_name,
            'dge_resource_display_name': helpers.dge_resource_display_name,
            'dge_get_dataset_publisher': helpers.dge_get_dataset_publisher,
            'dge_get_organization_administration_level_code': helpers.dge_get_organization_administration_level_code,
            'dge_get_dataset_administration_level': helpers.dge_get_dataset_administration_level,
            'dge_list_reduce_resource_format_label': helpers.dge_list_reduce_resource_format_label,
            'dge_theme_id': helpers.dge_theme_id,
            'dge_list_themes': helpers.dge_list_themes,
            'dge_dataset_display_frequency': helpers.dge_dataset_display_frequency,
            'dge_url_for_user_organization': helpers.dge_url_for_user_organization,
            'dge_resource_display_name_or_desc': helpers.dge_resource_display_name_or_desc,
            'dge_package_list_for_source': helpers.dge_package_list_for_source,
            'dge_api_swagger_url': helpers.dge_api_swagger_url,
            'dge_sparql_yasgui_endpoint': helpers.dge_sparql_yasgui_endpoint,
            'dge_resource_format_label': helpers.dge_resource_format_label,
            'dge_exported_catalog_files': helpers.dge_exported_catalog_files,
            'dge_get_endpoints_menu': helpers.dge_get_endpoints_menu,
            'dge_sort_alphabetically_resources': helpers.dge_sort_alphabetically_resources,
            'dge_dataset_tag_list_display_names': helpers.dge_dataset_tag_list_display_names,
            'dge_swagger_doc_url': helpers.dge_swagger_doc_url,
            'dge_sparql_yasgui_doc_url': helpers.dge_sparql_yasgui_doc_url,
            'dge_harvest_frequencies': helpers.dge_harvest_frequencies,
            'dge_get_facet_items_dict': helpers.dge_get_facet_items_dict,
            'dge_get_show_sort_facet': helpers.dge_get_show_sort_facet,
            'dge_default_facet_search_operator': helpers.dge_default_facet_search_operator,
            'dge_default_facet_sort_by_facet': helpers.dge_default_facet_sort_by_facet,
            'dge_add_additional_facet_fields': helpers.dge_add_additional_facet_fields,
            'dge_tag_link': helpers.dge_tag_link,
            'dge_searched_facet_item_filter': helpers.dge_searched_facet_item_filter,
            'get_available_locales':helpers.get_available_locales,
            'dge_generate_download_link':helpers.dge_generate_download_link,
            'dge_remove_field': helpers.dge_remove_field,
            'dge_get_recaptcha_public_key': helpers.dge_get_recaptcha_public_key,
            'dge_get_limit_to_download': helpers.dge_get_limit_to_download,
            'dge_load_dropdown_sections': helpers.dge_load_dropdown_sections,
            'dge_count_by_type_content_by_search': helpers.dge_count_by_type_content_by_search,
            'dge_get_selected_fields': helpers.dge_get_selected_fields,
            'dge_is_frontend': helpers.dge_is_frontend,
            'dge_load_json': helpers.dge_load_json,
            'dge_dump_json': helpers.dge_dump_json,
            'dge_field_display_subfields': helpers.dge_field_display_subfields,
            'dge_get_telephone_from_iri': helpers.dge_get_telephone_from_iri,
            'dge_get_email_from_iri': helpers.dge_get_email_from_iri,
            'dge_is_dcatapes': helpers.dge_is_dcatapes,
            'dge_is_hvd': helpers.dge_is_hvd,
            'dge_get_format_from_vocabulary_uri': helpers.dge_get_format_from_vocabulary_uri,
            'dge_get_include_fields': helpers.dge_get_include_fields,
            'dge_is_datosgobes_spatial_uri': helpers.dge_is_datosgobes_spatial_uri,
            'dge_is_datosgobes_theme_uri': helpers.dge_is_datosgobes_theme_uri,
            'dge_count_resources': helpers.dge_count_resources,
            'dge_get_vocabularies_uri_label': helpers.dge_get_vocabularies_uri_label,
            'dge_get_served_by_dataservice': helpers.dge_get_served_by_dataservice,
            'dge_get_datasets_served_by_dataservice': helpers.dge_get_datasets_served_by_dataservice,
            'dge_count_served_by_dataservice': helpers.dge_count_served_by_dataservice,
            'dge_has_resource_identification_info': helpers.dge_has_resource_identification_info,
            'dge_has_resource_interoperability_info': helpers.dge_has_resource_interoperability_info,
            'dge_has_resource_provenance_info': helpers.dge_has_resource_provenance_info,
            'dge_has_resource_reusability_info': helpers.dge_has_resource_reusability_info,
            'dge_has_package_information_info': helpers.dge_has_package_information_info,
            'dge_has_dataset_technical_sheet_info': helpers.dge_has_dataset_technical_sheet_info,
            'dge_has_package_contact_info': helpers.dge_has_package_contact_info,
            'dge_has_package_quality_info': helpers.dge_has_package_quality_info,
            'dge_get_count_active_package': helpers.dge_get_count_active_package,
            'dge_get_search_package_count': helpers.dge_get_search_package_count,
            'dge_has_guid': helpers.dge_has_guid,
            'dge_is_editable': helpers.dge_is_editable,
            'dge_get_nti_field_uri_label': helpers.dge_get_nti_field_uri_label,
            'dge_get_request_params_for_text_search': helpers.dge_get_request_params_for_text_search,
            'dge_url_for_broken_links': helpers.dge_url_for_broken_links,
            'dge_get_display_byte_size': helpers.dge_get_display_byte_size,
            'dge_display_dataservice_data': helpers.dge_display_dataservice_data
        }


    def before_index(self, data_dict):
        dataset = sh.scheming_get_schema('dataset', 'dataset')
        if ('res_format' in data_dict):
            formats = sh.scheming_field_by_name(dataset.get('resource_fields'),
                            'format')
            data_dict['res_format_label'] = []
            for res_format in data_dict['res_format']:
                if res_format == '':
                    data_dict['res_format_label'].append(dc.UNDEFINED_FORMAT_LABEL)
                else:
                    res_format_label = sh.scheming_choices_label(formats['choices'], res_format)
                    if res_format_label:
                        data_dict['res_format_label'].append(res_format_label)

        if ('publisher' in data_dict):
            organismo = data_dict['publisher']
            if helpers.dge_is_frontend():
                publisher = toolkit.get_action('dge_organization_publisher')({'model': model}, {'id': organismo})
            else:
                publisher = h.get_organization(organismo)
            data_dict['publisher'] = publisher.get('id')
            data_dict['publisher_display_name'] = publisher.get('display_name')
            administration_level_code = helpers.dge_get_organization_administration_level_code(publisher)
            if not administration_level_code or administration_level_code not in TRANSLATED_UNITS:
                administration_level_code = DEFAULT_UNIT
            data_dict['administration_level'] = administration_level_code
            data_dict['administration_level_es'] = TRANSLATED_UNITS[administration_level_code]['es'] or ''
            data_dict['administration_level_en'] = TRANSLATED_UNITS[administration_level_code]['en'] or ''
            data_dict['administration_level_ca'] = TRANSLATED_UNITS[administration_level_code]['ca'] or ''
            data_dict['administration_level_eu'] = TRANSLATED_UNITS[administration_level_code]['eu'] or ''
            data_dict['administration_level_gl'] = TRANSLATED_UNITS[administration_level_code]['gl'] or ''

        if ('theme' in data_dict):
            categoria = dsh.dge_get_nti_field_choices('theme')

            valor_categoria = data_dict['theme']
            data_dict['theme'] = []
            data_dict['theme_id'] = []
            data_dict['theme_es'] = []
            data_dict['theme_en'] = []
            data_dict['theme_ca'] = []
            data_dict['theme_eu'] = []
            data_dict['theme_gl'] = []

            valores = valor_categoria.replace('[','').replace(']','')
            categorias = valores.split('", "')
            for term_categoria in list(categorias):
                clean_term = term_categoria.replace('"','')
                data_dict['theme'].append(clean_term)
                data_dict['theme_id'].append(helpers.dge_theme_id(clean_term))
                for option in categoria:
                    if option['value'] == clean_term:
                        data_dict['theme_es'].append(option['label']['es'])
                        data_dict['theme_en'].append(option['label']['en'])
                        data_dict['theme_ca'].append(option['label']['ca'])
                        data_dict['theme_eu'].append(option['label']['eu'])
                        data_dict['theme_gl'].append(option['label']['gl'])

        data_dict['tags'] = set()
        if ('multilingual_tags' in data_dict):
            tags = json.loads(data_dict['multilingual_tags'])

            locale_order = config.get('ckan.locale_order', '').split()
            default_lang = None
            for lang in locale_order:
                if (lang in tags and tags[lang]):
                    default_lang = lang
                    break
            for lang in locale_order:
                tag_key = 'tags_' + lang
                data_dict[tag_key] = set()
                if (lang in tags and tags[lang]):
                    lang_tags = tags[lang]
                    for tag in lang_tags:
                        data_dict[tag_key].add(tag)
                elif default_lang:
                    lang_tags = tags[default_lang]
                    for tag in lang_tags:
                        data_dict[tag_key].add(tag + '__' + default_lang)     
                data_dict[tag_key] = list(data_dict[tag_key])

        data_dict['multilingual_tags'] = []
        
        if('hvd' in data_dict and data_dict['hvd'] == 'true'):
            data_dict['is_hvd'] = 'true'
        
        if ('frequency' in data_dict and 'type' in data_dict and data_dict['type'] == 'dataset'):
            frequency = json.loads(data_dict['frequency'])
            fidentifier = frequency.get('identifier', '')
            if not fidentifier:
                furi = frequency.get('uri', '')
                if furi:
                    fidentifier = furi[len(ds_constants.FREQUENCY_EUROPEAN_PREFIX):].lower()
                else:
                    ftype = frequency.get('type', '')
                    fvalue = frequency.get('value', '')
                    if ftype and fvalue:
                        fidentifier = dsh.dge_parse_frequency_identifier(ftype, fvalue)
                    else:
                        fidentifier = ds_constants.FREQUENCY_IDENTIFIER_OTHER
            if not fidentifier in ds_constants.FREQUENCY_IDENTIFIERS:
                fidentifier = ds_constants.FREQUENCY_IDENTIFIER_OTHER
            
            frequency_choices = dsh.dge_get_nti_field_choices('frequency')
            for frequency_choice in frequency_choices:
                if frequency_choice['value'] == fidentifier:
                    data_dict['frequency_label'] = fidentifier
                    data_dict['frequency_label_es'] = sh.scheming_language_text(frequency_choice['label'], 'es')
                    data_dict['frequency_label_en'] = sh.scheming_language_text(frequency_choice['label'], 'en')
                    data_dict['frequency_label_ca'] = sh.scheming_language_text(frequency_choice['label'], 'ca')
                    data_dict['frequency_label_gl'] = sh.scheming_language_text(frequency_choice['label'], 'gl')
                    data_dict['frequency_label_eu'] = sh.scheming_language_text(frequency_choice['label'], 'eu')

        return data_dict

    def frequency_format(self, fq):
        frequency_split= fq.split("{")[1].split ("}")[0]
        frequency_concat= "{" + frequency_split + "}"
        frequency_json = json.loads(frequency_concat)
        frec_final = "(%s AND %s)" %(frequency_json['type'], str(frequency_json['value']))
        frequency_replace_extra = fq.replace('frequency:', 'extras_frequency:')
        frequency_concat= '"%s"' %frequency_concat
        frequency_return = frequency_replace_extra.replace(frequency_concat, frec_final)

        return frequency_return
    
    def _facet_search_operator(self, fq, facet_field):
        new_fq = fq
        new_fq_list = []
        new_facet_field = facet_field

        try:
            default_facet_operator = helpers.dge_default_facet_search_operator()
            facet_operator = default_facet_operator
            try:
                if request is not None and request.params and list(request.params.items()):
                    if (FACET_OPERATOR_PARAM_NAME, 'AND') in list(request.params.items()):
                        facet_operator = 'AND'
                    elif (FACET_OPERATOR_PARAM_NAME, 'OR') in list(request.params.items()):
                        facet_operator = 'OR'
                    else:
                        facet_operator = default_facet_operator
            except Exception as e:
                log.warning("[_facet_search_operator]exception:%r: " % e)
                facet_operator = default_facet_operator

            if (facet_operator == 'OR'):
                pattern = re.compile(r'([+]?[\w.-]+:\(.*?\)|[+]?[\w.-]+:"[^"]*"|[+]?[\w.-]+:[^\s()]+)')
                condiciones = pattern.findall(fq)

                faceted_condiciones = []
                other_condiciones = []

                for cond in condiciones:
                    current_field = cond.lstrip('+-').split(':', 1)[0]
                    if current_field in facet_field:
                        faceted_condiciones.append(cond)
                    else:
                        other_condiciones.append(cond)

                if faceted_condiciones:
                    new_fq_list = [f"{{!tag=facets}}({' OR '.join(faceted_condiciones)})"]

                    new_fq = ''

                    if isinstance(facet_field, list):
                        new_facet_field = [f'{{!ex=facets}}{field}' for field in facet_field]
                    elif isinstance(facet_field, str):
                        new_facet_field = [f'{{!ex=facets}}{facet_field}']
                if other_condiciones:
                    new_fq = " ".join(other_condiciones)

        except UnicodeEncodeError as e:
            log.warning('UnicodeDecodeError %s  %s' % (e.errno, e.strerror))
        except:
            log.warning("Unexpected error:%r: " % sys.exc_info()[0])
            new_fq = fq
            new_fq_list = []
            new_facet_field = facet_field

        return new_fq, new_fq_list, new_facet_field

    def before_search(self, search_params):
        if not helpers.dge_is_frontend():
            return search_params

        order_by = search_params.get('sort', '')
        if not order_by:
            search_params['sort'] = 'score desc, metadata_created desc'

        new_fq, new_fq_list, new_facet_fields = self._facet_search_operator(
            (search_params.get('fq', '')), (search_params.get('facet.field', '')))
        search_params.update({'fq': new_fq})
        if 'fq_list' in search_params and search_params['fq_list']:
            search_params['fq_list'].extend(new_fq_list)
        else:
            search_params['fq_list'] = new_fq_list
        search_params.update({'facet.field': new_facet_fields})
   
        fq = search_params.get('fq', '')

        if "frequency" in fq:
          ''' This if is shared by datasets and harvest sources.
              Dataset's frequency facet are included with "{" and "}".
              Harvest's frequency doesn't, so checking is needed.'''
          if "{" in fq or "}" in fq:
              fq_new_frecuency = self.frequency_format(fq)
              search_params.update({'fq': fq_new_frecuency})
        if fq and fq.find('+dataset_type:harvest') > -1:
            orgs = toolkit.get_action('organization_list_for_user')(data_dict={'permission': 'read'})
            if orgs:
                org_ids = ''
                for org_tuple in orgs:
                    org_ids = '{0} OR {1}'.format(org_ids, org_tuple['id'])
                if len(org_ids) > 4:
                    org_ids = org_ids[4:]
                    fq = '{0} +owner_org:({1})'.format(fq, org_ids)
                else:
                    fq = '{0} -owner_org:[\'\' TO *]'.format(fq, '')
            else:
                fq = '{0} -owner_org:[\'\' TO *]'.format(fq, '')
            search_params.update({'fq': fq})

        fq = fq + ' +state:(draft OR active)'
        search_params.update({'fq': fq})
        
        search_params['defType'] = 'edismax'
        search_params['qf'] = "name^4 title^4 publisher_display_name^4 tags^2 groups^2 text"

        return search_params

    def after_search(self, search_results, search_params):
        if not helpers.dge_is_frontend():
            return search_results
        facets = search_results.get('search_facets')
        if not facets:
            return search_results

        desired_lang_code = toolkit.request.environ.get('CKAN_LANG')
        fallback_lang_code = config.get('ckan.locale_default', 'es')

        dict_categoria = {}
        for option in dsh.dge_get_nti_field_choices('theme'):
            label_option = (option.get('label')).get(desired_lang_code, None)
            if not label_option:
                 label_option = (option.get('label')).get(fallback_lang_code, None)
            dict_categoria[helpers.dge_theme_id(option.get('value'))] = label_option
        facet = facets.get('theme_id', None)
        if facet:
            facet_items_filtered = []
            for item in facet.get('items', None):
                if dict_categoria.get(item.get('name')):
                    item['display_name'] = dict_categoria.get(item.get('name'))
                    item['class'] = item.get('name')
                    facet_items_filtered.append(item)
            facet['items'] = facet_items_filtered
            
        dict_frequency = {}
        for option in dsh.dge_get_nti_field_choices('frequency'):
            label_option = (option.get('label')).get(desired_lang_code, None)
            if not label_option:
                 label_option = (option.get('label')).get(fallback_lang_code, None)
            dict_frequency[option.get('value')] = label_option
        facet = facets.get('frequency_label', None)
        if facet:
            for item in facet.get('items', None):
                item['display_name'] = dict_frequency.get(item.get('name'), item.get('display_name'))
        
        facet = facets.get('res_format_label', None)
        if facet:
            for item in facet.get('items', None):
                item['display_name'] = helpers.dge_resource_format_label(item.get('name'))
                item['format_class'] = item.get('name')

        facet = facets.get('administration_level', None)
        if facet:
            for item in facet.get('items', None):
                item['display_name'] = helpers.dge_get_translated_administration_level(item.get('name'))
                item['administration'] = item.get('name')

        tag_key = 'tags_' + (desired_lang_code or fallback_lang_code)
        facet = facets.get(tag_key, None)
        if facet:
            for item in facet.get('items', None):
                if ('__' in item.get('name')):
                    lang_index = item.get('name').index('__')
                    item['display_name'] = item.get('name')[:lang_index]
                    item['lang'] = item.get('name')[lang_index+2:]

        return search_results
    
    def before_view(self, pkg_dict):
        if 'type' in pkg_dict and pkg_dict['type'] == 'dataservice':
            pkg_dict['dataservice_pkgs'] = helpers.dge_get_datasets_served_by_dataservice(pkg_dict['id'])
        if 'type' in pkg_dict and pkg_dict['type'] == 'harvest':
            self._check_custom_authorization_for_harvester(pkg_dict)
        return pkg_dict

    def _check_custom_authorization_for_harvester(self, pkg_dict):
        context = {'model': model, 'session': model.Session,
                'user': c.user or c.author, 'for_view': True,
                'auth_user_obj': c.userobj}
        try:
            logic.check_access('dge_harvest_source_show', context, pkg_dict)
        except toolkit.NotAuthorized:
            abort(401, _('Not authorized to see this page'))

    def after_update(self, context, resource):
        if 'package' in list(context.keys()):
            package_name = context['package'].name
            package_id = context['package'].id
            if 'package_id' in list(resource.keys()):
                resource_package_id = resource['package_id']
                resource_id = resource['id']
                if resource_package_id == package_id:
                    h.redirect_to('package.resource_read',
                                id=package_name, resource_id=resource_id)
