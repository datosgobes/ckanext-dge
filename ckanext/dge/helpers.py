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

import ckanext.dge_scheming.helpers as dsh
import ckanext.dge_scheming.constants as ds_constants
import ckanext.dge.constants as constants
import ckanext.scheming.helpers as sh
from ckan.plugins.toolkit import (config, get_action)
import pytz
import datetime
import ckan.lib.helpers as h
import ckan.plugins.toolkit as toolkit
import json
import ast
from ckan import logic
from ckan.common import (_, g, c, request, json)
from operator import itemgetter
import ckan.model as model
from ckanext.harvest.helpers import get_harvest_source
from ckanext.dge_harvest.helpers import dge_harvest_get_vocabulary_element_label_dict
from ckan.lib.i18n import get_available_locales
import requests
from ckantoolkit import h as tkh
from sqlalchemy import create_engine, text

import io
import csv
from flask import Response
import logging


FACET_OPERATOR_PARAM_NAME = '_facet_operator'
FACET_SORT_PARAM_NAME = '_%s_sort'
DATASET_ALLOWED_FACETS = [
    'is_hvd',
    'theme_id',
    'res_format_label',
    'publisher_display_name',
    'administration_level',
    'frequency_label',
    'tags_es'
]
DATASERVICE_ALLOWED_FACETS = [
    'is_hvd',
    'theme_id',
    'publisher_display_name',
    'is_hvd'
]

TRANSLATED_UNITS = {'E': { 'es': 'Administraci\\u00F3n del Estado',
                           'ca': 'Administraci\\u00F3 de l\\u0027Estat',
                           'gl': 'Administraci\\u00F3n do Estado',
                           'eu': 'Estatuko Administrazioa',
                           'en': 'State Administration'}, \
                    'A': { 'es': 'Administraci\\u00F3n Auton\\u00F3ica',
                           'ca': 'Administraci\\u00F3 Auton\\u00F3mica',
                           'gl': 'Administraci\\u00F3n Auton\\u00F3mica',
                           'eu': 'Administrazio Autonomikoa',
                           'en': 'Regional Administration'},
                    'L': { 'es': 'Administraci\\u00F3n Local',
                           'ca': 'Administraci\\u00F3 Local',
                           'gl': 'Administraci\\u00F3n Local',
                           'eu': 'Toki Administrazioa',
                           'en': 'Local Administration'},
                    'U': { 'es': 'Universidades',
                           'ca': 'Universitats',
                           'gl': 'Universidades',
                           'eu': 'Unibertsitateak',
                           'en': 'Universities'},
                    'I': { 'es': 'Otras Instituciones',
                           'ca': 'Altres institucions',
                           'gl': 'Outras instituci\\u00F3ns',
                           'eu': 'Beste instituzio batzuk',
                           'en': 'Other Institutions'},
                    'J': { 'es': 'Administraci\\u00F3n de Justicia',
                           'ca': 'Administraci\\u00F3 de Just\\u00EDcia',
                           'gl': 'Administraci\\u00F3n de Xustiza',
                           'eu': 'Justizia Administrazioa',
                           'en': 'Legal Administration'},
                    'P': { 'es': 'Entidad Privada',
                           'ca': 'Entitat privada',
                           'gl': 'Entidade Privada',
                           'eu': 'Erakunde pribatua',
                           'en': 'Private Entity'}
                 }

DEFAULT_UNIT =  'I'




log = logging.getLogger(__name__)

def dge_default_locale():
    return config.get('ckan.locale_default', 'es').lower()

def dge_is_downloadable_resource(resource_url, resource_format=None):
    '''
    :param resource_url: resource access url
    :type string

    Returns True if resource_url does not end with a format included in
    ckanext.dge.no.downloadable.formats config properties or
    resource_format is not included in kanext.dge.no.downloadable.formats config properties.
    Otherwise False.
    '''
    result = True
    no_downloadable_formats = config.get('ckanext.dge.no.downloadable.formats', '').lower().split()
    resource_format_url = None
    if no_downloadable_formats and len(no_downloadable_formats) > 0:
        if resource_url is not None:
            split_resource_url = resource_url.lower().split('.')
            if len(split_resource_url) > 0:
                resource_format_url = split_resource_url[-1]

        if (resource_format_url is not None and \
            resource_format_url in no_downloadable_formats) or \
           (resource_format is not None \
            and resource_format.lower() in no_downloadable_formats):
            result = False

    return result

def dge_dataset_field_value(text):
    """
    :param text: {lang: text} dict or text string

    Convert "language-text" to users' language by looking up
    language in dict or using gettext if not a dict but. If the text
    doesn't exist look for an available text
    """
    value = None
    language = None
    if not text:
        result = ''

    dict_text = dsh.dge_dataset_form_lang_and_value(text)
    if (dict_text):
        language = sh.lang()
        if (language in dict_text and dict_text[language] and \
            dict_text[language].strip() != ''):
            value = dict_text[language]
            language = None
        else:
            for key in dict_text:
                if (dict_text[key] and dict_text[key].strip() != ''):
                    value = (dict_text[key])
                    language = key
                    break
    return language, value

def dge_dataset_display_fields(field_name_list, dataset_fields):
    """
    :param field_name_list: list of scheme field names
    :param dataset_fields:  fields of dataset

    Return a dictionary with field names in field_name_list and
    value field in scheme. None if field not exists in scheme
    """
    dataset_dict = {}
    if field_name_list:
        for field_name in field_name_list:
            dataset_dict[field_name] = None

        if dataset_fields:
            for field in dataset_fields:
                if field and field['field_name'] and field['field_name'] in field_name_list:
                    dataset_dict[field['field_name']] = field
    return dataset_dict


def dge_dataset_tag_field_value(tags):
    """
    :param tags: {lang: tags}

    Convert "language-text" to users' language by looking up
    language in dict or using gettext if not a dict but. If the text
    doesn't exist look for an available text
    """
    value = None
    language = None
    if not tags:
        result = ''

    dict_tags = dsh.dge_dataset_form_lang_and_value(tags)
    if (dict_tags):
        language = sh.lang()
        if language in dict_tags and dict_tags[language] and \
            dict_tags[language] is not None:
            value = dict_tags[language]
            language = None
        else:
            locale_order = config.get('ckan.locale_order', '').split()
            for l in locale_order:
                if l in dict_tags and dict_tags[l] and \
                    dict_tags[l] is not None:
                    value = (dict_tags[l])
                    language = l
                    break

    return language, value

def dge_render_datetime(datetime_, date_format=None, with_hours=False):
    '''Render a datetime object or timestamp string as a localised date or
    in the requested format.
    If timestamp is badly formatted, then a blank string is returned.

    :param datetime_: the date
    :type datetime_: datetime or ISO string format
    :param date_format: a date format
    :type date_format: string
    :param with_hours: should the `hours:mins` be shown
    :type with_hours: bool

    :rtype: string
    '''
    datetime_ = dge_parse_datetime(datetime_)
    if not datetime_ or datetime_ == '':
        return datetime_

    if date_format:
        try:
            return datetime_.strftime(date_format)
        except ValueError as e:
            log.info('%s has not correct value for strtime: %s' %
                     (datetime_, e))

    to_timezone = pytz.timezone('UTC')
    datetime_ = datetime_.astimezone(tz=to_timezone)

    details = {
        'min': datetime_.minute,
        'hour': datetime_.hour,
        'day': datetime_.day,
        'year': datetime_.year,
        'month': datetime_.month,
        'timezone': datetime_.tzinfo.zone,
    }
    if with_hours:
        result = ('{day}/{month:02}/{year} {hour:02}:{min:02} ({timezone})').format(**details)
    else:
        result = ('{day}/{month:02}/{year}').format(**details)
    return result


def dge_parse_datetime(datetime_=None):
    '''Parse a datetime object or timestamp string as a localised date.
    If timestamp is badly formatted, then a blank string is returned.

    :param datetime_: the date
    :type datetime_: datetime or ISO string format
    :rtype: datetime
    '''
    if not datetime_:
        return ''
    if isinstance(datetime_, str):
        try:
            datetime_ = h.date_str_to_datetime(datetime_)
        except TypeError:
            return None
        except ValueError:
            return None
    if not isinstance(datetime_, datetime.datetime):
        return None

    from_timezone = pytz.timezone('Europe/Madrid')
    return from_timezone.localize(datetime_)



def dge_dataset_display_name(package_or_package_dict):
    """
    Get title and language of a package

    :param package_or_package_dict: the package
    :type dict or package:

    :rtype string, string: translated title, and locale
    """
    if isinstance(package_or_package_dict, dict):
        language, value = dge_dataset_field_value(package_or_package_dict.get('title_translated'))
    else:
        language, value = dge_dataset_field_value(package_or_package_dict.title_translated)
    return value

def dge_resource_display_name(resource_or_resource_dict):
    """
    Get title and language of a resource

    :param resource_or_resource_dict: the resource
    :type dict or resource:

    :rtype string, string: translated title, and locale
    """
    if isinstance(resource_or_resource_dict, dict):
        language, value = dge_dataset_field_value(resource_or_resource_dict.get('name_translated'))
    else:
        language, value = dge_dataset_field_value(resource_or_resource_dict.name_translated)
    if value:
        return value
    else:
        return _("Unnamed resource")

def dge_get_dataset_publisher(org=None):
    '''
    Given an organization id, returns a dict:
     key='name' -> the organization title
     key='title' -> the organization title
     key='subname' -> the principal organization title
     key= 'administration_level' -> administration level of the organization

    :param org: organization id
    :type string
    '''
    if org is None:
        return {}
    try:
        result = {}
        organization = get_action('dge_organization_publisher')({'model': model}, {'id': org})
        if organization:
            result['NAME'] = organization['title'] or organization['name']
            if organization['extras']:
                for extra in organization['extras']:
                    if extra and extra['key'] == 'C_DNM_DEP_UD_PRINCIPAL' \
                            and extra['value']:
                        result['PPAL_NAME'] = extra['value']
                    elif extra and extra['key'] == 'C_ID_UD_ORGANICA' \
                            and extra['value']:
                        result['AL'] = dge_get_dataset_administration_level(None, extra['value'])
    except:
        return None
    return result


def dge_get_dataset_administration_level(org=None, id_ud_organic=None):
    '''
    Given an id_ud_organic, returns the administration level according
    to the first letter of id_ud_organic
    Given an organization , returns the administration level according
    to the first letter of its extra C_ID_UD_ORGANICA

    :param org: organization id
    :type string

    :param id_ud_organic: id_ud_organic
    :type string
    '''
    if org is None and id_ud_organic is None:
        return {}
    try:
        result = {}
        if id_ud_organic and len(id_ud_organic) > 0:
            value = id_ud_organic[0].upper()
            if value:
                value_translated = dge_get_translated_administration_level(value)
                if value_translated:
                    return value_translated
        elif org:
            organization = get_action('dge_organization_publisher')({'model': model}, {'id': org})
            value = dge_get_organization_administration_level_code(organization)
            if value:
                value_translated = dge_get_translated_administration_level(value)
                if value_translated:
                    return value_translated
    except :
       return {}

    return result

def dge_get_organization_administration_level_code(organization=None):
    if organization is None:
        return {}
    try:
        result = None
        if (organization and organization['extras']):
            for extra in organization['extras']:
                if extra and extra['key'] == 'C_ID_UD_ORGANICA' \
                   and extra['value']:
                    result = extra['value'][0].upper()
    except :
        return None
    return result

def dge_get_translated_dataset_administration_level(organization=None, lang='es'):
    '''
    Given an organization id, returns values of extra C_ID_UD_ORGANICA

    :param organization: organization id
    :type string

    :param lang: locale
    :type string
    '''
    if organization is None:
        return {}
    try:
        result = None
        value = dge_get_organization_administration_level_code(organization)
        if value and value in TRANSLATED_UNITS:
            return TRANSLATED_UNITS[value][lang]
        else:
            return TRANSLATED_UNITS[DEFAULT_UNIT][lang]
    except :
        return None
    return result

def dge_list_reduce_resource_format_label(resources=None, field_name='format'):
    '''
    Given an resource list, get label of resource_format

    :param resources: resource dict
    :type dict list

    :param field_name: field_name of resource
    :type string

    :rtype string list
    '''

    format_list = h.dict_list_reduce(resources, field_name)
    dataset = sh.scheming_get_schema('dataset', 'dataset')
    formats = sh.scheming_field_by_name(dataset.get('resource_fields'),
                'format')
    label_list = []
    for res_format in format_list:
        res_format_label = sh.scheming_choices_label(formats['choices'], res_format)
        if res_format_label:
            label_list.append(res_format_label)
    return label_list

def dge_resource_format_label(res_format=None):
    '''
    Given an format, get its label

    :param res_format: format
    :type string

    :rtype string
    '''
    if format:
        if res_format and res_format == constants.UNDEFINED_FORMAT_LABEL:
            res_format_label = sh.scheming_language_text(ds_constants.UNDEFINED_FORMAT_LABELS)
            if res_format_label:
                return res_format_label
        else:
            dataset = sh.scheming_get_schema('dataset', 'dataset')
            formats = sh.scheming_field_by_name(dataset.get('resource_fields'),
                    'format')
            res_format_label = sh.scheming_choices_label(formats['choices'], res_format)
            if res_format_label:
                return res_format_label
    return res_format

def dge_theme_id(theme=None):
    '''
    Given a value of theme, returs its identifier
    :param theme: value theme
    :type string

    :rtype string
    '''
    id = None
    if theme:
        index = theme.rfind('/')
        if (index > -1 and (index+1 < len(theme))):
            id = theme[index+1:]
    return id

def dge_list_themes(themes=None):
    '''
    Given an theme list values, get theirs translated labels
    for the NTI-RISP themes

    :param themes: value theme list
    :type string list

    :rtype (string, string) list
    '''
    label_list = []
    for theme in themes:
        if dge_is_datosgobes_theme_uri(theme):
            label = sh.scheming_choices_label(dsh.dge_get_nti_field_choices('theme'), theme)
            if label:
                label_list.append((dge_theme_id(theme), label))
    return label_list

def dge_dataset_display_frequency(fvalue, ftype, furi, fidentifier):
    '''
    Given a value and type frequency, get the translated label

    :param fvalue: value of frequency
    :type int

    :param ftype: type of frequency
    :type string
    
    :param furi: uri of frequency
    :type string
    
    :param fidentifier: identifier of frequency
    :type string

    :rtype string (frequency label)
    '''
    fidentifier = fidentifier if fidentifier else ds_constants.FREQUENCY_IDENTIFIER_OTHER
    types = ['seconds', 'minutes', 'hours', 'days', 'weeks', 'months', 'years']
    if fidentifier == ds_constants.FREQUENCY_IDENTIFIER_OTHER and fvalue and ftype and ftype in types:
        return _('Every {time_value} {time_unit}').format(time_value=fvalue, time_unit=_(ftype))
    else:
        frequency_choices = dsh.dge_get_nti_field_choices('frequency')
        for frequency_choice in frequency_choices:
            if frequency_choice['value'] == fidentifier:
                return sh.scheming_language_text(frequency_choice['label'])
        return sh.scheming_language_text(ds_constants.FREQUENCY_STANDARD_LABELS_DEFAULT)

def dge_url_for_user_organization():
    ''' Returns the link to the Organization in which the user active is editor '''
    if getattr(g, u'user', None):
        if c.userobj.sysadmin:
            endpoint = 'organization.index'
            if dge_is_frontend():
                endpoint = 'dgeOrganization.organizations_index'
            return h.url_for(endpoint)
        else:
            orgs = get_action('organization_list_for_user')(data_dict={'permission': 'read'})
            if orgs and len(orgs) > 0:
                return '/catalogo?publisher_display_name=' + orgs[0].get('title')
    return None

def dge_resource_display_name_or_desc(name=None, description=None):
    '''
    Given a resource name, returns resourcename,
          else returns given resource description

    :param name: resource name
    :type string

    :param stype: resource description
    :type string

    :rtype string (resource display name)
    '''
    if name:
        return name
    elif description:
        description = description.split('.')[0]
        max_len = 60
        if len(description) > max_len:
            description = description[:max_len] + '...'
        return description
    else:
        return _("Unnamed resource")

def dge_package_list_for_source(source_id):
    '''
    Creates a dataset list with the ones belonging to a particular harvest
    source.

    It calls the package_list snippet and the pager.
    '''
    DATASET_TYPE_NAME = 'harvest'
    limit = 20
    page = int(request.args.get('page', 1))

    fq = 'harvest_source_id:"{0}"'.format(source_id)
    search_dict = {
        'fq' : fq,
        'rows': limit,
        'sort': 'metadata_modified desc',
        'start': (page - 1) * limit,
    }

    context = {'model': model, 'session': model.Session}

    harvest_source = get_harvest_source(source_id)
    owner_org = harvest_source.get('owner_org', '')

    if owner_org:
        user_member_of_orgs = [org['id'] for org
                   in h.organizations_available('read')]
        if (harvest_source and owner_org in user_member_of_orgs):
            context['ignore_capacity_check'] = True

    query = logic.get_action('package_search')(context, search_dict)

    base_url = h.url_for('{0}.read'.format(DATASET_TYPE_NAME), id=source_id)
    def pager_url(q=None, page=None):
        url = base_url
        if page:
            url += '?page={0}'.format(page)
        return url

    pager = h.Page(
        collection=query['results'],
        page=page,
        url=pager_url,
        item_count=query['count'],
        items_per_page=limit
    )
    pager.items = query['results']

    if query['results']:
        out = h.snippet('snippets/dge_package_list.html', packages=query['results'])
        out += pager.pager()
    else:
        out = h.snippet('snippets/package_list_empty.html')

    return out

def dge_api_swagger_url():
    '''
    Returns endpoint of swagger, set in ckanext.dge.api.swagger.url config property.
    Returns emtpy string if property does not exist.
    '''
    return h.url_for_static_or_external(config.get('ckanext.dge.api.swagger.url', '').lower())

def dge_sparql_yasgui_endpoint():
    '''
    Returns endpoint of sparql, set in ckanext.dge.api.yasgui.url config property.
    Returns emtpy string if property does not exist.
    '''
    return h.url_for_static_or_external(config.get('ckanext.dge.sparql.yasgui.endpoint', '').lower())

def dge_swagger_doc_url(lang = None):
    '''
    Returns url of swagger documentation page,
    set in ckanext.dge.api.swagger.doc.url config property.
    Returns emtpy string if property does not exist.
    '''
    prefix = None
    url = config.get('ckanext.dge.api.swagger.doc.url', None)
    if not lang:
        lang = config.get('ckan.locale_default', 'es')
    if url and lang:
        if (url.startswith('/')):
            prefix = ('/' + lang + url).lower()
        else:
            prefix = ('/' + lang + '/' + url).lower()
    return prefix

def dge_sparql_yasgui_doc_url(lang = None):
    '''
    Returns url of sparql documentation page,
    set in ckanext.dge.sparql.yasgui.doc.url config property.
    Returns emtpy string if property does not exist.
    '''

    prefix = None
    url = config.get('ckanext.dge.sparql.yasgui.doc.url', None)
    if not lang:
        lang = config.get('ckan.locale_default', 'es')
    if url and lang:
        if (url.startswith('/')):
            prefix = ('/' + lang + url).lower()
        else:
            prefix = ('/' + lang + '/' + url).lower()
    return prefix

def dge_get_translated_administration_level(prefix=None):
    '''
    Given a prefix of administration level,
    returns translated administration level
    '''
    units = {'E': _('State Administration'),
             'A': _('Regional Administration'),
             'L': _('Local Administration'),
             'U': _('Universities'),
             'I': _('Other Institutions'),
             'J': _('Legal Administration'),
             'P': _('Private Entity')
            }
    if prefix and prefix in units:
        return units.get(prefix, None)
    else:
        return units.get(DEFAULT_UNIT, None)
    return None

def dge_exported_catalog_files():
    '''
    Returns endpoint of download catalog files in rdf, csv and atom format
    '''
    url_rdf = config.get('ckanext.dge.catalog.export.rdf.url', None)
    url_csv = config.get('ckanext.dge.catalog.export.csv.url', None)
    url_atom = config.get('ckanext.dge.catalog.export.atom.url', None)
    return url_rdf, url_csv, url_atom

def dge_get_endpoints_menu(keys=[], lang=None, header=True, footer=False):
    ''' get endpoint for drupal submenu elements
    :param keys: properties keys
    :type keys: list

    :param lang: locale for endpoints. It must be a locale_order
    :type lang: string

    :param header: if true, get endpoints for header drupal submenu elements
    :type header: boolean

    :param footer: if true, get endpoints for footer drupal submenu elements
    :type footer: boolean

    :rtype: dict with key, property key and value the endpoint
    '''
    menu = {}
    if not lang:
        lang = config.get('ckan.locale_default', None)
        if not lang:
            log.debug('empty or None local')
            return {}
    prefix = '/' + lang

    user_logged_page = config.get('ckan.site_url', '') + prefix + '/user/login'
    index = user_logged_page.find('://')
    if (index >= 0):
        user_logged_page = 'https' + user_logged_page[index:]

    menu['ckanext.dge.user_logged_page'] = user_logged_page
    menu['ckanext.dge.drupal_menu.home'] = prefix + '/home'
    menu['ckanext.dge.drupal_menu.aporta.about'] = prefix + '/acerca-de-la-iniciativa-aporta'
    menu['ckanext.dge.drupal_menu.aporta.meetings'] = prefix + '/encuentros-aporta'
    menu['ckanext.dge.drupal_menu.aporta.challenge'] = prefix + '/desafios-aporta'
    menu['ckanext.dge.drupal_menu.aporta.awards'] = prefix + '/premios-aporta'
    menu['ckanext.dge.drupal_menu.impact.success_cases'] = prefix + '/casos-exito'
    menu['ckanext.dge.drupal_menu.interact.documentation'] = prefix + '/documentacion'
    menu['ckanext.dge.drupal_menu.interact.requests'] = prefix + '/peticiones-datos'
    menu['ckanext.dge.drupal_menu.interact.about'] = prefix + '/informa-sobre'
    menu['ckanext.dge.drupal_menu.news.risp'] = prefix + '/comunidad-risp'
    menu['ckanext.dge.drupal_menu.account.profile'] = prefix + '/user'
    menu['ckanext.dge.drupal_menu.account.requests'] = prefix + '/admin/dashboard/requests'
    menu['ckanext.dge.drupal_menu.account.applications'] = prefix + '/admin/dashboard/apps'
    menu['ckanext.dge.drupal_menu.account.success_cases'] = prefix + '/admin/dashboard/success'
    menu['ckanext.dge.drupal_menu.account.unassigned_requests'] = prefix + '/admin/dashboard/unassigned-requests'
    menu['ckanext.dge.drupal_menu.account.initiatives'] = prefix + '/admin/dashboard/initiatives'
    menu['ckanext.dge.drupal_menu.account.comments'] = prefix + '/admin/dashboard/comment'
    menu['ckanext.dge.drupal_menu.account.media'] = prefix + '/admin/dashboard/media'
    menu['ckanext.dge.drupal_menu.account.widget'] = prefix + '/admin/dashboard/widget'
    menu['ckanext.dge.drupal_menu.account.users'] = prefix + '/admin/people/'
    menu['ckanext.dge.drupal_menu.account.logout'] = prefix + '/user/logout'
    menu['ckanext.dge.drupal_menu.proteccion_datos'] = 'http://www.red.es/redes/es/quienes-somos/protecci%C3%B3n-de-datos-de-car%C3%A1cter-personal'
    menu['ckanext.dge.drupal_menu.cookies_policy'] = prefix + '/politica-de-cookies'
    menu['ckanext.dge.drupal_menu.sectors.environment'] = prefix + '/sector/medio-ambiente'
    menu['ckanext.dge.drupal_menu.sectors.culture_and_leisure'] = prefix + '/sector/cultura-ocio'
    menu['ckanext.dge.drupal_menu.sectors.education'] = prefix + '/sector/educacion'
    menu['ckanext.dge.drupal_menu.sectors.transport'] = prefix + '/sector/transporte'
    menu['ckanext.dge.drupal_menu.sectors.health'] = prefix + '/sector/salud-bienestar'
    menu['ckanext.dge.drupal_menu.sectors.tourism'] = prefix + '/sector/turismo'
    menu['ckanext.dge.drupal_menu.sectors.justice'] = prefix + '/sector/justicia-sociedad'


    menu['ckanext.dge.drupal_menu.contact_email'] = config.get('ckanext.dge.drupal_menu_footer.contact_email','')



    if prefix == '/en':

        menu['ckanext.dge.drupal_menu.open_data_catalogue'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.open_data_catalogue', '/catalogo')
        menu['ckanext.dge.drupal_menu.data_request'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.data_request', '/data-request')
        menu['ckanext.dge.drupal_menu.support_for_publishers'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.support_for_publishers', '/advice-and-support')
        menu['ckanext.dge.drupal_menu.data_spaces'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.data_spaces', '/data-spaces')
        menu['ckanext.dge.drupal_menu.safe_environments'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.safe_environments', '/safe-environments')

        menu['ckanext.dge.drupal_menu.initiatives'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.initiatives', '/initiatives')
        menu['ckanext.dge.drupal_menu.applications'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.applications', '/applications')
        menu['ckanext.dge.drupal_menu.companies'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.companies','/companies')
        menu['ckanext.dge.drupal_menu.sectors'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.sectors','/sectors')
        menu['ckanext.dge.drupal_menu.challenges'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.challenges','/aporta-challenge')

        menu['ckanext.dge.drupal_menu.news'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.news','/news')
        menu['ckanext.dge.drupal_menu.events'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.events','/events')

        menu['ckanext.dge.drupal_menu.blog'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.blog','/blog')
        menu['ckanext.dge.drupal_menu.data_exercises'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.data_exercises','/conocimiento/tipo/data-exercises')
        menu['ckanext.dge.drupal_menu.infographics'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.infographics','/conocimiento/tipo/infographics')
        menu['ckanext.dge.drupal_menu.interviews'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.interviews','/interviews')
        menu['ckanext.dge.drupal_menu.reports_and_guides'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.reports_and_guides','/conocimiento/tipo/reports-and-studies/tipo/guides/tipo/training-materials/tipo/regulations-and-strategies')
        menu['ckanext.dge.drupal_menu.github_datosgob'] = config.get('ckanext.dge.drupal_menu_header_en.github_datosgob','https://github.com/datosgobes')
        menu['ckanext.dge.drupal_menu.aporta_meetings'] = config.get('ckanext.dge.drupal_menu_header_en.aporta_meetings','/aporta-meetings')

        menu['ckanext.dge.drupal_menu.what_we_do'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.what_we_do','/what-we-do')
        menu['ckanext.dge.drupal_menu.metrics_and_impact'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.metrics_and_impact','/metrics-and-impact')
        menu['ckanext.dge.drupal_menu.frequently_asked_questions'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.frequently_asked_questions','/preguntas-frecuentes/faq_categoria/general')
        menu['ckanext.dge.drupal_menu.technology'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.technology','/technology')
        menu['ckanext.dge.drupal_menu.form.contact'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.form.contact','/contact')
        menu['ckanext.dge.drupal_menu.sitemap'] = prefix + config.get('ckanext.dge.drupal_menu_header_en.sitemap','/sitemap')


        menu['ckanext.dge.drupal_menu.legal_notice'] = prefix + config.get('ckanext.dge.drupal_menu_footer_en.legal_notice','/legal-notice')
        menu['ckanext.dge.drupal_menu.accesibility'] = prefix + config.get('ckanext.dge.drupal_menu_footer_en.accesibility','/accessibility')
        menu['ckanext.dge.drupal_menu.subscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_en.subscribe','/newsletter-subscription')
        menu['ckanext.dge.drupal_menu.unsubscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_en.unsubscribe','/formulario-de-baja')


    elif prefix == '/ca':

        menu['ckanext.dge.drupal_menu.open_data_catalogue'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.open_data_catalogue', '/catalogo')
        menu['ckanext.dge.drupal_menu.data_request'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.data_request', '/sollicitud-de-dades')
        menu['ckanext.dge.drupal_menu.support_for_publishers'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.support_for_publishers', '/assessorament-i-suport')
        menu['ckanext.dge.drupal_menu.data_spaces'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.data_spaces', '/espais-de-dades')
        menu['ckanext.dge.drupal_menu.safe_environments'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.safe_environments', '/entorns-segurs')

        menu['ckanext.dge.drupal_menu.initiatives'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.initiatives','/iniciatives')
        menu['ckanext.dge.drupal_menu.applications'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.applications','/aplicacions')
        menu['ckanext.dge.drupal_menu.companies'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.companies','/empreses')
        menu['ckanext.dge.drupal_menu.sectors'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.sectors','/sectors')
        menu['ckanext.dge.drupal_menu.challenges'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.challenges','/desafiament-aporta')

        menu['ckanext.dge.drupal_menu.news'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.news','/noticies')
        menu['ckanext.dge.drupal_menu.events'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.events', '/esdeveniments')

        menu['ckanext.dge.drupal_menu.blog'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.blog','/blog')
        menu['ckanext.dge.drupal_menu.data_exercises'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.data_exercises','/conocimiento/tipo/exercicis-de-dades')
        menu['ckanext.dge.drupal_menu.infographics'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.infographics','/conocimiento/tipo/infografies')
        menu['ckanext.dge.drupal_menu.interviews'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.interviews','/entrevistes')
        menu['ckanext.dge.drupal_menu.reports_and_guides'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.reports_and_guides','/conocimiento/tipo/informes-i-estudis/tipo/guies/tipo/materials-formatius/tipo/normatives-i-estrategies')
        menu['ckanext.dge.drupal_menu.github_datosgob'] = config.get('ckanext.dge.drupal_menu_header_ca.github_datosgob')
        menu['ckanext.dge.drupal_menu.aporta_meetings'] = config.get('ckanext.dge.drupal_menu_header_ca.aporta_meetings','/trobades-aporta')


        menu['ckanext.dge.drupal_menu.what_we_do'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.what_we_do','/que-fem')
        menu['ckanext.dge.drupal_menu.metrics_and_impact'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.metrics_and_impact','/metriques-i-impacte')
        menu['ckanext.dge.drupal_menu.frequently_asked_questions'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.frequently_asked_questions','/preguntas-frecuentes/faq_categoria/generals')
        menu['ckanext.dge.drupal_menu.technology'] = prefix +  config.get('ckanext.dge.drupal_menu_header_ca.technology','/tecnologia')
        menu['ckanext.dge.drupal_menu.form.contact'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.form.contact','/contacte')
        menu['ckanext.dge.drupal_menu.sitemap'] = prefix + config.get('ckanext.dge.drupal_menu_header_ca.sitemap','/mapa-del-lloc')


        menu['ckanext.dge.drupal_menu.legal_notice'] = prefix + config.get('ckanext.dge.drupal_menu_footer_ca.legal_notice','/avis-legal')
        menu['ckanext.dge.drupal_menu.accesibility'] = prefix + config.get('ckanext.dge.drupal_menu_footer_ca.accesibility','/accessibilitat')
        menu['ckanext.dge.drupal_menu.subscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_ca.subscribe','/subscripcio-al-butlleti')
        menu['ckanext.dge.drupal_menu.unsubscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_ca.unsubscribe','/formulario-de-baja')


    elif prefix == '/eu':

        menu['ckanext.dge.drupal_menu.open_data_catalogue'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.open_data_catalogue', '/catalogo')
        menu['ckanext.dge.drupal_menu.data_request'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.data_request', '/datuak-eskatzea')
        menu['ckanext.dge.drupal_menu.support_for_publishers'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.support_for_publishers', '/aholkularitza-eta-laguntza')
        menu['ckanext.dge.drupal_menu.data_spaces'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.data_spaces', '/datuen-eremua')
        menu['ckanext.dge.drupal_menu.safe_environments'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.safe_environments', '/ingurune-seguruak')

        menu['ckanext.dge.drupal_menu.initiatives'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.initiatives', '/ekimenen')
        menu['ckanext.dge.drupal_menu.applications'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.applications','/aplikazioak')
        menu['ckanext.dge.drupal_menu.companies'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.companies','/enpresak')
        menu['ckanext.dge.drupal_menu.sectors'] = prefix +  config.get('ckanext.dge.drupal_menu_header_eu.sectores','/sektoreak')
        menu['ckanext.dge.drupal_menu.challenges'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.challenges','/aporta-sariak')

        menu['ckanext.dge.drupal_menu.news'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.news','/berriak')
        menu['ckanext.dge.drupal_menu.events'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.events','/gertaerak')

        menu['ckanext.dge.drupal_menu.blog'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.blog','/bloga')
        menu['ckanext.dge.drupal_menu.data_exercises'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.data_exercises','/conocimiento/tipo/datuen-erabilerak')
        menu['ckanext.dge.drupal_menu.infographics'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.infographics','/conocimiento/tipo/infografiak')
        menu['ckanext.dge.drupal_menu.interviews'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.interviews','/elkarrizketak')
        menu['ckanext.dge.drupal_menu.reports_and_guides'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.reports_and_guides','/conocimiento/tipo/txostenak-eta-ikerketak/tipo/gidak/tipo/prestakuntza-materialak/tipo/araudia-eta-estrategiak')
        menu['ckanext.dge.drupal_menu.github_datosgob'] = config.get('ckanext.dge.drupal_menu_header_eu.github_datosgob')
        menu['ckanext.dge.drupal_menu.aporta_meetings'] = config.get('ckanext.dge.drupal_menu_header_eu.aporta_meetings','/aporta-bilerak')

        menu['ckanext.dge.drupal_menu.what_we_do'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.what_we_do','/zer-egiten-dugu')
        menu['ckanext.dge.drupal_menu.metrics_and_impact'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.metrics_and_impact','/metrikoak-eta-inpaktua')
        menu['ckanext.dge.drupal_menu.presencia_en_RRSS_EN'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.presencia_en_RRSS_EN','/presencia-en-rrss-eu')
        menu['ckanext.dge.drupal_menu.frequently_asked_questions'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.frequently_asked_questions','/preguntas-frecuentes/faq_categoria/orokorra')
        menu['ckanext.dge.drupal_menu.technology'] = prefix +  config.get('ckanext.dge.drupal_menu_header_eu.technology','/teknologia')
        menu['ckanext.dge.drupal_menu.form.contact'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.form.contact','/kontaktua')
        menu['ckanext.dge.drupal_menu.sitemap'] = prefix + config.get('ckanext.dge.drupal_menu_header_eu.sitemap','/webgunearen-mapa')


        menu['ckanext.dge.drupal_menu.legal_notice'] = prefix + config.get('ckanext.dge.drupal_menu_footer_eu.legal_notice','/lege-oharra')
        menu['ckanext.dge.drupal_menu.accesibility'] = prefix + config.get('ckanext.dge.drupal_menu_footer_eu.accesibility','/irisgarritasuna')
        menu['ckanext.dge.drupal_menu.subscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_eu.subscribe','/buletinen-harpidetza')
        menu['ckanext.dge.drupal_menu.unsubscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_eu.unsubscribe','/formulario-de-baja')


    elif prefix == '/gl':
        menu['ckanext.dge.drupal_menu.open_data_catalogue'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.open_data_catalogue', '/catalogo')
        menu['ckanext.dge.drupal_menu.data_request'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.data_request', '/solicitude-de-datos')
        menu['ckanext.dge.drupal_menu.support_for_publishers'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.support_for_publishers', '/asesoramento-e-soporte')
        menu['ckanext.dge.drupal_menu.data_spaces'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.data_spaces', '/espazos-de-datos')
        menu['ckanext.dge.drupal_menu.safe_environments'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.safe_environments', '/interfaces-seguras')

        menu['ckanext.dge.drupal_menu.initiatives'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.initiatives','/iniciativas')
        menu['ckanext.dge.drupal_menu.applications'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.applications', '/aplicacions')
        menu['ckanext.dge.drupal_menu.companies'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.companies','/empresas')
        menu['ckanext.dge.drupal_menu.sectors'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.sectors','/sectores')
        menu['ckanext.dge.drupal_menu.challenges'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.challenges','/desafios-aporta')

        menu['ckanext.dge.drupal_menu.news'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.news','/noticias')
        menu['ckanext.dge.drupal_menu.events'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.events','/eventos')

        menu['ckanext.dge.drupal_menu.blog'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.blog','/blog')
        menu['ckanext.dge.drupal_menu.data_exercises'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.data_exercises','/conocimiento/tipo/exercicios-de-datos')
        menu['ckanext.dge.drupal_menu.infographics'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.infographics','/conocimiento/tipo/infografias')
        menu['ckanext.dge.drupal_menu.interviews'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.interviews','/entrevistas')
        menu['ckanext.dge.drupal_menu.reports_and_guides'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.reports_and_guides','/conocimiento/tipo/informes-e-estudos/tipo/guias/tipo/materiais-formativos/tipo/normativa-e-estratexias')
        menu['ckanext.dge.drupal_menu.github_datosgob'] = config.get('ckanext.dge.drupal_menu_header_gl.github_datosgob')
        menu['ckanext.dge.drupal_menu.aporta_meetings'] = config.get('ckanext.dge.drupal_menu_header_gl.aporta_meetings','/encontros-achega')


        menu['ckanext.dge.drupal_menu.what_we_do'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.what_we_do','/que-facemos')
        menu['ckanext.dge.drupal_menu.metrics_and_impact'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.metrics_and_impact','/metricas-e-impacto')
        menu['ckanext.dge.drupal_menu.frequently_asked_questions'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.frequently_asked_questions','/preguntas-frecuentes/faq_categoria/xeral')
        menu['ckanext.dge.drupal_menu.technology'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.technology','/tecnoloxia')
        menu['ckanext.dge.drupal_menu.form.contact'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.form.contact','/contacto')
        menu['ckanext.dge.drupal_menu.sitemap'] = prefix + config.get('ckanext.dge.drupal_menu_header_gl.sitemap','/mapa-do-sitio')

        menu['ckanext.dge.drupal_menu.legal_notice'] = prefix + config.get('ckanext.dge.drupal_menu_footer_gl.legal_notice','/aviso-legal-gl')
        menu['ckanext.dge.drupal_menu.accesibility'] = prefix + config.get('ckanext.dge.drupal_menu_footer_gl.accesibility','/accesibilidade')
        menu['ckanext.dge.drupal_menu.subscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_gl.subscribe','/subscricion-ao-boletin-informativo')
        menu['ckanext.dge.drupal_menu.unsubscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_gl.unsubscribe','/formulario-de-baja')



    else:

        menu['ckanext.dge.drupal_menu.open_data_catalogue'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.open_data_catalogue', '/catalogo')
        menu['ckanext.dge.drupal_menu.data_request'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.data_request', '/solicitud-de-datos')
        menu['ckanext.dge.drupal_menu.support_for_publishers'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.support_for_publishers', '/apoyo-a-publicadores')
        menu['ckanext.dge.drupal_menu.data_spaces'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.data_spaces', '/espacios-de-datos')
        menu['ckanext.dge.drupal_menu.safe_environments'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.safe_environments', '/entornos-tratamiento-seguros')

        menu['ckanext.dge.drupal_menu.initiatives'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.initiatives','/iniciativas')
        menu['ckanext.dge.drupal_menu.applications'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.applications', '/aplicaciones')
        menu['ckanext.dge.drupal_menu.companies'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.companies','/empresas-reutilizadoras')
        menu['ckanext.dge.drupal_menu.sectors'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.sectors','/sectores')
        menu['ckanext.dge.drupal_menu.challenges'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.challenges','/desafio-aporta')

        menu['ckanext.dge.drupal_menu.news'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.news','/noticias')
        menu['ckanext.dge.drupal_menu.events'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.events','/eventos')
        menu['ckanext.dge.drupal_menu.newsletters'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.newsletters','/boletines')

        menu['ckanext.dge.drupal_menu.blog'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.blog','/blog')
        menu['ckanext.dge.drupal_menu.data_exercises'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.data_exercises','/conocimiento/tipo/ejercicios-de-datos')
        menu['ckanext.dge.drupal_menu.infographics'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.infographics','/conocimiento/tipo/infografias')
        menu['ckanext.dge.drupal_menu.interviews'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.interviews','/entrevistas')
        menu['ckanext.dge.drupal_menu.reports_and_guides'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.reports_and_guides','/conocimiento/tipo/informes-y-estudios/tipo/guias/tipo/materiales-formativos/tipo/normativas-y-estrategias')
        menu['ckanext.dge.drupal_menu.github_datosgob'] = config.get('ckanext.dge.drupal_menu_header_es.github_datosgob')
        menu['ckanext.dge.drupal_menu.aporta_meetings'] = config.get('ckanext.dge.drupal_menu_header_es.aporta_meetings','/encuentros-aporta')

        menu['ckanext.dge.drupal_menu.what_we_do'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.what_we_do','/que-hacemos')
        menu['ckanext.dge.drupal_menu.metrics_and_impact'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.metrics_and_impact','/metricas-e-impacto')
        menu['ckanext.dge.drupal_menu.presencia_en_RRSS_EN'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.presencia_en_RRSS_EN','/presencia-en-rrss')
        menu['ckanext.dge.drupal_menu.frequently_asked_questions'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.frequently_asked_questions','/preguntas-frecuentes/faq_categoria/generales')
        menu['ckanext.dge.drupal_menu.technology'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.technology','/tecnologia')
        menu['ckanext.dge.drupal_menu.form.contact'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.form.contact','/form/contact')
        menu['ckanext.dge.drupal_menu.sitemap'] = prefix + config.get('ckanext.dge.drupal_menu_header_es.sitemap','/mapa-del-sitio')

        menu['ckanext.dge.drupal_menu.legal_notice'] = prefix + config.get('ckanext.dge.drupal_menu_footer_es.legal_notice','/aviso-legal')
        menu['ckanext.dge.drupal_menu.accesibility'] = prefix + config.get('ckanext.dge.drupal_menu_footer_es.accesibility','/accesibilidad')
        menu['ckanext.dge.drupal_menu.subscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_es.subscribe','/formulario-de-alta')
        menu['ckanext.dge.drupal_menu.unsubscribe'] = prefix + config.get('ckanext.dge.drupal_menu_footer_es.unsubscribe','/formulario-de-baja')





    if (keys and len(keys) > 0) or header or footer:
        locales_order = config.get('ckan.locale_order', None)

        lorder = []
        if locales_order:
            lorder = locales_order.split();
            index = lorder.index(lang)
            if (index == -1):
                log.debug('locale not found %s', lang)
                return {}

        if header or footer:
            if 'ckanext.dge.drupal_menu.aporta.about' not in keys:
                keys.append('ckanext.dge.drupal_menu.aporta.about')
            if 'ckanext.dge.drupal_menu.aporta.meetings' not in keys:
                keys.append('ckanext.dge.drupal_menu.aporta.meetings')
            if 'ckanext.dge.drupal_menu.aporta.challenge' not in keys:
                keys.append('ckanext.dge.drupal_menu.aporta.challenge')
            if 'ckanext.dge.drupal_menu.aporta.awards' not in keys:
                keys.append('ckanext.dge.drupal_menu.aporta.awards')
            if 'ckanext.dge.drupal_menu.impact.initiatives' not in keys:
                keys.append('ckanext.dge.drupal_menu.impact.initiatives')
            if 'ckanext.dge.drupal_menu.impact.applications' not in keys:
                keys.append('ckanext.dge.drupal_menu.impact.applications')
            if 'ckanext.dge.drupal_menu.impact.success_cases' not in keys:
                keys.append('ckanext.dge.drupal_menu.impact.success_cases')
            if 'ckanext.dge.drupal_menu.interact.documentation' not in keys:
                keys.append('ckanext.dge.drupal_menu.interact.documentation')
            if 'ckanext.dge.drupal_menu.interact.advise_support' not in keys:
                keys.append('ckanext.dge.drupal_menu.interact.advise_support')
            if 'ckanext.dge.drupal_menu.interact.requests' not in keys:
                keys.append('ckanext.dge.drupal_menu.interact.requests')
            if 'ckanext.dge.drupal_menu.interact.about' not in keys:
                keys.append('ckanext.dge.drupal_menu.interact.about')
            if 'ckanext.dge.drupal_menu.news.news' not in keys:
                keys.append('ckanext.dge.drupal_menu.news.news')
            if 'ckanext.dge.drupal_menu.newsletters' not in keys:
                keys.append('ckanext.dge.drupal_menu.newsletters')
            if 'ckanext.dge.drupal_menu.news.events' not in keys:
                keys.append('ckanext.dge.drupal_menu.news.events')
            if 'ckanext.dge.drupal_menu.news.risp' not in keys:
                keys.append('ckanext.dge.drupal_menu.news.risp')

        if header:
            if 'ckanext.dge.drupal_menu.account.profile' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.profile')
            if 'ckanext.dge.drupal_menu.account.requests' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.requests')
            if 'ckanext.dge.drupal_menu.account.applications' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.applications')
            if 'ckanext.dge.drupal_menu.account.success_cases' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.success_cases')
            if 'ckanext.dge.drupal_menu.account.unassigned_requests' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.unassigned_requests')
            if 'ckanext.dge.drupal_menu.account.comments' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.comments')
            if 'ckanext.dge.drupal_menu.account.initiatives' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.initiatives')
            if 'ckanext.dge.drupal_menu.account.widget' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.widget')
            if 'ckanext.dge.drupal_menu.account.media' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.media')
            if 'ckanext.dge.drupal_menu.account.users' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.users')
            if 'ckanext.dge.drupal_menu.account.logout' not in keys:
                keys.append('ckanext.dge.drupal_menu.account.logout')

        if footer:
            if 'ckanext.dge.drupal_menu.sitemap' not in keys:
                keys.append('ckanext.dge.drupal_menu.sitemap')
            if 'ckanext.dge.drupal_menu.contact' not in keys:
                keys.append('ckanext.dge.drupal_menu.contact')
            if 'ckanext.dge.drupal_menu.legal_notice' not in keys:
                keys.append('ckanext.dge.drupal_menu.legal_notice')
            if 'ckanext.dge.drupal_menu.faq' not in keys:
                keys.append('ckanext.dge.drupal_menu.faq')
            if 'ckanext.dge.drupal_menu.subscribe' not in keys:
                keys.append('ckanext.dge.drupal_menu.subscribe')
            if 'ckanext.dge.drupal_menu.unsubscribe' not in keys:
                keys.append('ckanext.dge.drupal_menu.unsubscribe')
            if 'ckanext.dge.drupal_menu.cookies_policy' not in keys:
                keys.append('ckanext.dge.drupal_menu.cookies_policy')
            if 'ckanext.dge.drupal_menu.technology' not in keys:
                keys.append('ckanext.dge.drupal_menu.technology')


        for key in keys:
            value = config.get(key, None)
            svalue = None
            if value:
                svalue = value.split(';')
            if svalue:
                if len(svalue) == 1:
                    menu[key] = prefix + svalue[0]
                elif len(svalue) > index:
                    menu[key] = prefix + svalue[index]
    return menu

def dge_sort_alphabetically_resources(resources = None, is_samples=False):
    if not resources:
        return
    filtered_resources = []
    new_resources = []

    for res in resources:
        is_sample = res.get('is_sample', None)
        if is_samples and is_sample:
            filtered_resources.append(res)
        if not is_samples and not is_sample:
            filtered_resources.append(res)
    for res in filtered_resources:
        language, value= dge_dataset_field_value(res.get('name_translated'))
        if not value:
            value = _("Unnamed resource")
        new_res = {'lang': language, 'value': value, 'resource': res}
        new_resources.append(new_res)
    sorted_resources = sorted(new_resources, key=itemgetter('value'), reverse=False)
    return sorted_resources

def dge_dataset_tag_list_display_names(tags=None):
    ''' get a list of tags display_name separated by commas
    :param keys: tags
    :type keys: list

    :rtype: string with display_name of tags separated by commas
    '''
    result = ""
    if tags:
        for tag in tags:
            if tag and tag.get('display_name'):
                result = result + "," + tag.get('display_name')
    if result and len(result)>0:
        return result[1:]

def dge_transform_archiver_dict(archiver):
    ''' get a list of tags display_name separated by commas
    :param keys: tags
    :type keys: list

    :rtype: string with display_name of tags separated by commas
    '''
    return ast.literal_eval(archiver)

def dge_harvest_frequencies():
    '''returns a list with all the possible frequencies for harvesting as dge
    '''
    return [{'text': toolkit._(f.title()), 'value': f}
            for f in constants.DGE_HARVEST_UPDATE_FREQUENCIES]


def dge_get_show_sort_facet(facet_name):
    '''returns true if the facet sort type should be displayed, false otherwise
    '''
    return dge_facet_property_default_value('ckanext.dge.facet.default.show_sort', facet_name, False)

def dge_get_facet_items_dict(facet, limit=None, exclude_active=False, default_sort=True):
    '''Return the list of unselected facet items for the given facet, sorted
    by count or by index.

    Returns the list of unselected facet contraints or facet items (e.g. tag
    names like "russian" or "tolstoy") for the given search facet (e.g.
    "tags"), sorted by facet item count (i.e. the number of search results that
    match each facet item).

    Reads the complete list of facet items for the given facet from
    c.search_facets, and filters out the facet items that the user has already
    selected.

    Arguments:
    facet -- the name of the facet to filter.
    limit -- the max. number of facet items to return.
    exclude_active -- only return unselected facets.
    default_sort -- return default ckan sort (count).
    '''

    if not c.search_facets or \
            not c.search_facets.get(facet) or \
            not c.search_facets.get(facet).get('items'):
        return []
    facets = []
    args = request.args.to_dict(flat=False).get(facet) if request.args.to_dict(flat=False).get(facet) != None else []
    for facet_item in c.search_facets.get(facet)['items']:
        if not len(facet_item['name'].strip()):
            continue
        if not facet_item['name'] in args:
            facets.append(dict(active=False, **facet_item))
        elif not exclude_active:
            facets.append(dict(active=True, **facet_item))

    sort = 'count'
    if default_sort == False:
        if ((FACET_SORT_PARAM_NAME % facet, 'index') in list(request.params.items())):
            sort = 'index'
        elif ((FACET_SORT_PARAM_NAME % facet, 'count') in list(request.params.items())):
            sort = 'count'
        else:
            sort = dge_default_facet_sort_by_facet(facet)

    if sort == 'index':
        facets = sorted(facets, key=lambda item: _(item['display_name']), reverse=False)
    else:
        facets = sorted(facets, key=lambda item: item['count'], reverse=True)

    if c.search_facets_limits and limit is None:
        limit = c.search_facets_limits.get(facet)
        if limit == 0:
            limit = int(dge_facet_property_default_value('ckanext.dge.facet.default.limit', facet, limit))

    if limit is not None and limit > 0:
        return facets[:limit]
    return facets

def dge_default_facet_search_operator():
    '''Returns the default facet search operator: AND/OR
    '''
    facet_operator = config.get('ckanext.dge.facet.default.search.operator', '')
    if facet_operator and (facet_operator.upper() == 'AND' or facet_operator.upper() == 'OR'):
        facet_operator = facet_operator.upper()
    else:
        facet_operator = 'AND'
    return facet_operator

def dge_default_facet_sort_by_facet(facet):
    ''' Returns the default facet sort. Content by default '''
    return dge_facet_property_default_value('ckanext.dge.facet.default.sort', facet, 'content')

def dge_facet_property_default_value(property_prefix, facet, default_value):
    ''' Returns the value of the first property found for one for a given facet
        following the order, or the default value in case it does not exist:
            - property_prefix.facet
            - property_prefix.facet_without_language
            - property_prefix

        Params:
            property_prefix: the property prefix
            facet: facet name
            default_value: property default value
    '''
    property_value = None
    if property_prefix is None:
        return None
    if facet is not None:
        property_value = config.get(('%s.%s' % (property_prefix, facet)), None)
        facet_no_lang = dge_get_facet_without_lang(facet)
        if property_value is None and facet != facet_no_lang:
            property_value = config.get(('%s.%s' % (property_prefix, facet_no_lang)), None)
    if property_value is None:
        property_value = config.get(('%s' % property_prefix), default_value)

    return property_value

def dge_get_facet_without_lang(facet):
    ''' Returns facet's name without lang '''
    suffix = '_%s' % h.lang()
    if facet is not None and facet.endswith(suffix):
        len_suffix = len(suffix)
        return facet[:-len_suffix]
    else:
        return facet

def dge_add_additional_facet_fields(fields, facets):
    ''' Add fields liked to facet sort or conjunction/disjunction
    '''
    param_keys = [FACET_OPERATOR_PARAM_NAME]
    if facets:
        for facet in facets:
            param_keys.append(FACET_SORT_PARAM_NAME % facet)
    if list(request.params.items()):
        for (k,v) in list(request.params.items()):
            if k in param_keys:
                fields.append((k,v))
    return fields
def dge_tag_link(tag, language = None):
    '''
    Generate the URL of a tag, taking into account of the language

    :param tag: the tag
    :type tag: string or unicode

    :param language: the tag language
    :type language: string

    :rtype string: URL for the provided tag
    '''

    iface_language = sh.lang()
    tags_tag = 'tags_' + iface_language
    pos_tag = '__' + language if (language and language != iface_language) else ''

    arguments = {
        tags_tag: tag + pos_tag
    }
    return h.url_for('package.search', **arguments)


def dge_searched_facet_item_filter(list_, search_field, output_field, value, facet_field):
    ''' Takes a list of dicts and returns the item of a given key if the
    item has a matching value for a supplied key

    :param list_: the list to search through for matching items
    :type list_: list of dicts

    :param search_field: the key to use to find matching items
    :type search_field: string

    :param value: the value to search for

    :param output_field: the key to use to output the value
    :type output_field: string

    :param facet_field: the facet_field
    :type search_field: string
    '''
    display_name = None
    lang = None
    item = None
    if list_:
        for list_item in list_:
            if list_item.get(search_field) == value:
                item = list_item

    if item != None:
        lang = item.get('lang', None)
        display_name = item.get(output_field) or item.get(search_field)
    else:
        if facet_field and facet_field.startswith('tags_'):

            value_ = value.split('__')
            display_name = value_[0]
            if len(value_) == 2:
                lang = value_[1]
        else:
            display_name = h.list_dict_filter(list_, search_field, output_field, value)

    return display_name, lang


def dge_generate_download_link(url, params):
    params = params.to_dict(flat=False)
    for idx, param in enumerate(params):
        if idx == 0:
            url += '?'
        if len(params.get(param)) > 1:
            url += param + '=['
            for item in params.get(param):
                item = item.replace(',', '%2C')
                url += item.replace(' ', '+') + '%2C'
            url = url[:-3] + ']&'
        else:
            item = params.get(param)[0].replace(',', '%2C')
            url += param+'='+item.replace(' ', '+')+'&'

    url = url[:-1] if params else url
    return url.replace(' ', '%20')


def dge_get_recaptcha_public_key():
    return config.get('ckan.recaptcha.publickey', None)


def dge_get_limit_to_download():
    return int(config.get('ckanext.dge.download_csv_limit', ''))


def dge_remove_field(controller, key, value=None, replace=None):
    if controller == 'organization' :
        return h.remove_url_param(key, value=value, replace=replace, controller=controller, action=u'read', extras=dict(id=g.group_dict.get(u'name')))
    else:
        action = '{0}.search'.format(controller)
        return h.remove_url_param(key, value=value, replace=replace, alternative_url=h.url_for(action))


def dge_load_dropdown_sections(lang=None):


    menu = {}
    if not lang:
        lang = config.get('ckan.locale_default', None)
        if not lang:
            log.debug('empty or None local')
            return {}
    prefix = 'ckanext.sections_texts_'+ lang + '_'

    if prefix == 'ckanext.sections_texts__':
        prefix = 'ckanext.sections_texts_es_'


    items_dropdown = []

    def get_custom_url(key, lang):
      if key == 'data_exercises':
        if lang == 'es':
          return 'conocimiento/tipo/ejercicios-de-datos'
        elif lang == 'en':
          return 'conocimiento/tipo/data-exercises'
        elif lang == 'ca':
          return 'conocimiento/tipo/exercicis-de-dades'
        elif lang == 'gl':
          return 'conocimiento/tipo/exercicios-de-datos'
        elif lang == 'eu':
          return 'conocimiento/tipo/datuen-erabilerak'
        else:
          return 'conocimiento/tipo/ejercicios-de-datos'
      elif key == 'infographics':
        if lang == 'es':
          return 'conocimiento/tipo/infografias'
        elif lang == 'en':
          return 'conocimiento/tipo/infographics'
        elif lang == 'ca':
          return 'conocimiento/tipo/infografies'
        elif lang == 'gl':
          return 'conocimiento/tipo/infografias'
        elif lang == 'eu':
          return 'conocimiento/tipo/infografiak'
        else:
          return 'conocimiento/tipo/infografias'
      elif key == 'reports_and_guides':
        if lang == 'es':
          return 'conocimiento/tipo/informes-y-estudios/tipo/guias/tipo/materiales-formativos/tipo/normativas-y-estrategias'
        elif lang == 'en':
          return 'conocimiento/tipo/reports-and-studies/tipo/guides/tipo/training-materials/tipo/regulations-and-strategies'
        elif lang == 'ca':
          return 'conocimiento/tipo/informes-i-estudis/tipo/guies/tipo/materials-formatius/tipo/normatives-i-estrategies'
        elif lang == 'gl':
          return 'conocimiento/tipo/informes-e-estudos/tipo/guias/tipo/materiais-formativos/tipo/normativa-e-estratexias'
        elif lang == 'eu':
          return 'conocimiento/tipo/txostenak-eta-ikerketak/tipo/gidak/tipo/prestakuntza-materialak/tipo/araudia-eta-estrategiak'
        else:
          return 'conocimiento/tipo/informes-y-estudios/tipo/guias/tipo/materiales-formativos/tipo/normativas-y-estrategias'
      return None


    keys = [
      'all_sections', 'datasets', 'use_cases', 'blog',
      'data_exercises', 'infographics', 'reports_and_guides', 'companies', 'interviews', 'events',
      'initiatives', 'news', 'data_request'
    ]

    translated_keys = {}
    for key in keys:
        config_key_generic = f'ckanext.sections_keys_{key}'
        if config_key_generic in toolkit.config:
            translated_keys[key] = toolkit.config[config_key_generic]


    custom_keys = {
      prefix + key: (get_custom_url(key, lang) if key in ['data_exercises', 'infographics', 'reports_and_guides'] else translated_keys.get(key))
      for key in keys
    }

    for key in toolkit.config:
        if key.startswith(prefix):
            value = toolkit.config[key]
            custom_key = custom_keys.get(key)
            if custom_key:
                if custom_key == 'all_sections':
                    items_dropdown.append({
                        'custom_key': '',
                        'value': value
                    })
                elif custom_key == 'datasets':
                    items_dropdown.append({
                        'custom_key': 'custom_content_type_ckan',
                        'value': value
                    })
                else:
                    items_dropdown.append({
                        'custom_key': custom_key,
                        'value': value
                    })


    first_two = items_dropdown[:2]
    sorted_items = sorted(items_dropdown[2:], key=lambda item: item['value'])
    items_dropdown = first_two + sorted_items

    return items_dropdown

def getTabsFromApiDrupal(lang=None,search_query=None):

    url = config.get('ckan.site_url_ip')+'/'+lang+'/v1/search?text='+search_query

    try:
        cert_path = config.get('requests.verify.ca_cert.path', '')
        response = requests.get(url, verify=cert_path)
        response.raise_for_status()
        data = response.json()
        return data
    except requests.exceptions.RequestException as e:
        log.error(f'Error fetching Drupal content search from {url}: {e}')
        return None

def dge_count_by_type_content_by_search(lang=None, search_query=None):

    tabs = getTabsFromApiDrupal(lang,search_query)
    if tabs is not None:  
        markup = tabs.get('#markup', '')
    else:
        markup = ''
    return markup

def dge_get_selected_fields(keys_to_ignore):
    ''' Get the reqest attributes and return a list of fields ready
    to be used with form.hidden_from_list
    '''
    return [(key, value) for key, values in request.args.to_dict(flat=False).items() for value in values if key not in keys_to_ignore]


def dge_is_frontend():
    is_frontend = False
    config_is_frontend = config.get('ckanext.dge.is_frontend', None)
    if config_is_frontend and config_is_frontend.lower() == 'true':
        is_frontend = True
    return is_frontend



def descargar_csv():
    api_key = request.headers.get('Authorization')
    ckan_user_id = request.args.get('ckan_user_id')
    
    if not c.userobj or (c.userobj and not c.userobj.sysadmin):
        return toolkit.abort(403, _('Not authorized to see this page'))
    
    if not ckan_user_id:
        return toolkit.abort(400, _('Missing value: User id'))

    request_user = model.Session.query(model.User).filter_by(id=ckan_user_id).first()
    if not request_user:
        return toolkit.abort(404, _('User does not exist'))
    
    ckan_user_org_id = None
    context = {'user': request_user.name}
    orgs = get_action('organization_list_for_user')(context, data_dict={'permission': 'read'})
    if orgs and len(orgs) > 0:
        ckan_user_org_id = orgs[0].get('id')
    
    if not ckan_user_org_id:
        return toolkit.abort(403, _('Not authorized to see this page'))

    endpoint = request.path

    if endpoint == '/dashboard/more-view-dataset':
        csv_data = generar_csv_conjunto_datos_mas_vistos_publicador(ckan_user_org_id)
        filename = 'conjunto_datos_mas_vistos_publicador'
    elif endpoint == '/dashboard/content-dataset-evolution':
        csv_data = generar_csv_conjunto_datos_evolucion_publicador(ckan_user_org_id)
        filename = 'conjunto_datos_evolucion_publicador'
    elif endpoint == '/dashboard/content-dataset-distributions':
        csv_data = generar_csv_conjunto_datos_distribuciones_formato_publicador(ckan_user_org_id)
        filename = 'conjunto_datos_distribuciones_formato_publicador'
    elif endpoint == '/dashboard/content-comments-received':
        csv_data = generar_csv_contenidos_comentarios_recibidos_publicador(ckan_user_org_id)
        filename = 'contenidos_comentarios_recibidos_publicador'
    elif endpoint == '/dashboard/users-by-organization':
        csv_data = generar_csv_usuarios_por_organismo(ckan_user_org_id)
        filename = 'usuarios_por_organismo'
    elif endpoint == '/dashboard/content-data-request-by-state':
        csv_data = generar_csv_peticiones_datos_por_estado(ckan_user_org_id)
        filename = 'peticiones_datos_por_estado'
    else:
        log.error("Endpoint desconocido")
        return "Endpoint desconocido", 400

    response = Response(csv_data)
    response.headers['Content-Type'] = 'text/csv'
    response.headers['Content-Disposition'] = f'attachment; filename="{filename}.csv"'

    return response



def generar_csv_desde_sql(sql_query,ckan_user_org_id):
    """
    Genera un archivo CSV a partir de una consulta SQL.

    Args:
    - sql_query (str): Consulta SQL que devuelve los datos para el CSV.

    Returns:
    - str: El contenido CSV generado.
    """
    result = model.Session.execute(sql_query, {'ckan_user_org_id':ckan_user_org_id})
    rows = result.fetchall()
    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)
    columns = result.keys()
    writer.writerow(columns)

    for row in rows:
        writer.writerow(row)

    csv_content = output.getvalue()
    output.close()

    return csv_content

def generar_csv_desde_mysql(mysql_query,ckan_user_org_id):
    """
    Genera un archivo CSV a partir de una consulta SQL a Drupal.

    Args:
    - mysql_query (str): Consulta SQL a Drupal que devuelve los datos para el CSV.

    Returns:
    - str: El contenido CSV generado.
    """
    engine = create_engine(config.get('ckanext.dge_drupal_users.connection', None))
    result = None
    rows = []

    with engine.connect() as connection:
        result = engine.execute(mysql_query, {'ckan_user_org_id':ckan_user_org_id})

        rows = result.fetchall()

    output = io.StringIO()
    writer = csv.writer(output, quoting=csv.QUOTE_ALL)

    columns = result.keys() if result else []

    writer.writerow(columns)

    for row in rows:
        writer.writerow(row)

    csv_content = output.getvalue()

    output.close()

    return csv_content


def generar_csv_conjunto_datos_mas_vistos_publicador(ckan_user_org_id):
    sql = """
      select
			case
				when dgp.year_month = 'All' then 'Total acumulado'
				else (
	           	 TO_CHAR(TO_DATE(dgp.year_month, 'YYYY-MM'), 'TMMonth') || ' ' || TO_CHAR(TO_DATE(dgp.year_month, 'YYYY-MM'), 'YYYY') ||
	            	case
		           		when extract(month from	TO_DATE(dgp.year_month, 'YYYY-MM')) = 2	and dgp.end_day::INT in (28, 29) then ''
						when dgp.end_day::INT in (30, 31) then ''
						else ' (hasta el ' || dgp.end_day || ')'
					end
	        	)
			end as "Mes",
			'https://datos.gob.es/es/catalogo/' || dgp.package_name as "Url",
			case
				when p.title is not null
				and p.state = 'active' then p.title
				else '[Eliminado] ' || dgp.package_name
			end as "Conjunto de datos",
			case
				when p.title is not null
				and p.state = 'active' then 'Público'
				else ''
			end as "Público/Privado",
			coalesce(g.title, dgp.publisher_id) as "Publicador",
			dgp.pageviews as "Visitas",
			array_to_string(array_agg(distinct dgr.url || '(' || dgr.total_events || ')'),';') as "Recurso(Descargas)"
		from
			dge_ga_packages dgp
		left join dge_ga_resources dgr on dgr.organization_id = dgp.organization_id
			and dgr.package_name = dgp.package_name
			and dgr.year_month = dgp.year_month
		left join package p on p.name = dgp.package_name
		left join "group" g on g.id = dgp.organization_id
		where
			dgp.organization_id = :ckan_user_org_id
		group by
			dgp.organization_id,
			dgp.year_month,
			dgp.end_day,
			dgp.package_name,
			p.title,
			p.state,
			p.private,
			g.title,
			dgp.publisher_id,
			dgp.pageviews
		order by
			dgp.year_month desc,
			dgp.pageviews desc;
    """
    return generar_csv_desde_sql(sql,ckan_user_org_id)



def generar_csv_conjunto_datos_evolucion_publicador(ckan_user_org_id):
    sql = """
    select d.year_month as year, d.num_datasets as value
        from dge_dashboard_published_datasets d
        where "key" = 'organization_id' and key_value = :ckan_user_org_id
        order by year_month asc;
    """
    return generar_csv_desde_sql(sql,ckan_user_org_id)


def generar_csv_conjunto_datos_distribuciones_formato_publicador(ckan_user_org_id):
    sql = """
    select
			  TO_CHAR(NOW(), 'YYYY-MM-DD') as "date",
	    	  CASE r.format
			    WHEN 'text/csv' THEN 'CSV'
			    WHEN 'application/json' THEN 'JSON'
			    WHEN 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' THEN 'XLSX'
			    WHEN 'text/html' THEN 'HTML'
			    WHEN 'text/pc-axis' THEN 'PC-Axis'
			    WHEN 'application/vnd.ms-excel' THEN 'XLS'
			    WHEN 'application/pdf' THEN 'PDF'
			    WHEN 'image/png' THEN 'PNG'
			    WHEN 'text/tab-separated-values' THEN 'TSV'
			    WHEN 'text/xml' THEN 'XML'
			    WHEN 'application/xml' THEN 'XML'
			    WHEN 'image/jpeg' THEN 'JPG'
			    WHEN 'application/vnd.google-earth.kml+xml' THEN 'KML'
			    WHEN 'text/wms' THEN 'WMS'
			    WHEN 'image/tiff' THEN 'TIFF'
			    WHEN 'application/zip' THEN 'ZIP'
			    WHEN 'text/ascii' THEN 'ASCII'
			    WHEN 'text/plain' THEN 'plain'
			    WHEN 'application/api' THEN 'API'
			    WHEN 'application/x-zipped-shp' THEN 'SHP'
			    WHEN 'text/turtle' THEN 'RDF-Turtle'
			    WHEN 'application/vnd.oasis.opendocument.spreadsheet' THEN 'ODS'
			    WHEN 'application/rdf+xml' THEN 'RDF-XML'
			    WHEN 'application/vnd.google-earth.kmz' THEN 'KMZ'
			    WHEN 'application/vnd.geo+json' THEN 'GeoJSON'
			    WHEN 'application/gml+xml' THEN 'GML'
			    WHEN 'application/octet-stream' THEN 'OCTET-STREAM'
			    WHEN 'application/ld+json' THEN 'JSON-LD'
			    WHEN 'application/atom+xml' THEN 'Atom'
			    WHEN 'application/geopackage+sqlite3' THEN 'GeoPackage'
			    WHEN 'application/rss+xml' THEN 'RSS'
			    WHEN 'text/n3' THEN 'RDF-N3'
			    WHEN 'application/vnd.ogc.wms_xml' THEN 'WMS-XML'
			    WHEN 'application/scorm' THEN 'SCORM'
			    WHEN 'application/elp' THEN 'ELP'
			    WHEN 'application/x-turtle' THEN 'TURTLE'
			    WHEN 'text/rdf+n3' THEN 'N3'
			    WHEN 'application/netcdf' THEN 'NetCDF'
			    WHEN 'application/xhtml+xml' THEN 'XHTML'
			    WHEN 'application/sparql-query' THEN 'SPARQL'
			    WHEN 'application/x-zip-compressed' THEN 'ZIP'
			    WHEN 'application/geo+pdf' THEN 'GeoPDF'
			    WHEN 'application/geo+json' THEN 'GeoJSON'
			    WHEN 'text/wfs' THEN 'WFS'
			    WHEN 'application/javascript' THEN 'JSON-P'
			    WHEN 'application/gpx+xml' THEN 'GPX'
			    WHEN 'text/calendar' THEN 'Calendar'
			    WHEN 'application/gzip' THEN 'GZIP'
			    WHEN 'application/ecw' THEN 'ECW'
			    WHEN 'application/msaccess' THEN 'MDB'
			    WHEN 'image/vnd.dwg' THEN 'DWG'
			    WHEN 'application/vnd.oasis.opendocument.text' THEN 'ODT'
			    WHEN 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' THEN 'DOCX'
			    WHEN 'application/marc' THEN 'MARC'
			    WHEN 'application/x-tmx+xml' THEN 'TMX'
			    WHEN 'image/jp2' THEN 'JP2'
			    WHEN 'text/wcs' THEN 'WCS'
			    WHEN 'application/solr' THEN 'Solr'
			    WHEN 'image/vnd.djvu' THEN 'DjVu'
			    WHEN 'application/x-qgis' THEN 'QGIS'
			    WHEN 'application/msword' THEN 'DOC'
			    WHEN 'text/rtf' THEN 'RTF'
			    WHEN 'image/vnd.dgn' THEN 'DGN'
			    WHEN 'application/xbrl' THEN 'XBRL'
			    WHEN 'application/ecmascript' THEN 'ECMAScript'
			    WHEN 'application/las' THEN 'LAS'
			    WHEN 'application/x-json' THEN 'JSON'
			    WHEN 'application/x-rar-compressed' THEN 'RAR'
			    WHEN 'application/x-tbx+xml' THEN 'TBX'
			    WHEN 'application/vnd.apache.parquet' THEN 'Parquet'
			    WHEN 'image/svg+xml' THEN 'SVG'
			    WHEN 'application/dbf' THEN 'DBF'
			    WHEN 'application/epub+zip' THEN 'ePub'
			    WHEN 'application/sparql-results+xml' THEN 'SPARQL-XML'
			    WHEN 'text/xml+georss' THEN 'GeoRSS'
			    WHEN 'application/sparql-results+json' THEN 'SPARQL-JSON'
			    WHEN 'application/csw' THEN 'CSW'
			    WHEN 'application/dxf' THEN 'DXF'
			    WHEN 'x-lml/x-gdb' THEN 'GDB'
			    WHEN 'application/mp4' THEN 'MP4'
			    WHEN 'application/soap+xml' THEN 'SOAP'
			    ELSE r.format
			  END AS format,
	    	  count(p.title) as value
			from (select * from "group" where id = :ckan_user_org_id)grp
			inner join package p on p.owner_org = grp.id
			inner join resource r ON p.id = r.package_id
			where
	    	  p.type = 'dataset'
	    	  and p.state = 'active'
	    	  and p.private is false
	    	  and r.state = 'active'
			group by r.format
			order by value desc;
    """
    return generar_csv_desde_sql(sql,ckan_user_org_id)


def generar_csv_contenidos_comentarios_recibidos_publicador(ckan_user_org_id):
    sql = """
    select
		m.year_month as year,
		coalesce(SUM(case when d.content_type = 'content_comments' then num_contents else 0 end),
		0) as content_comments,
		coalesce(SUM(case when d.content_type = 'dataset_comments' then num_contents else 0 end),
		0) as dataset_comments
	from
		(
		select
			distinct(year_month)
		from
			dge_dashboard_drupal_contents
		where
			(year_month not like '2012%'
				and year_month not like '2013%'
				and year_month not like '2014%'
				and year_month not like '2015%'
				and year_month not like '2016-0%'
				and year_month not like '2016-10%')) m
	left join
	  (
		select
			*
		from
			dge_dashboard_drupal_contents
		where
			key = 'org'
			and key_value = :ckan_user_org_id)d on
		d.year_month = m.year_month
	group by
		m.year_month
	order by
		m.year_month;
    """
    return generar_csv_desde_sql(sql,ckan_user_org_id)


def generar_csv_usuarios_por_organismo(ckan_user_org_id):
    sql = """
    select
        TO_CHAR(NOW(), 'dd/MM/yyyy') as "Fecha de actualización de los datos",
        u.name as "Nombre de usuario"
    from
        "member" m
    inner join "user" u on
        u.id = m.table_id
    where
        m.table_name = 'user'
        and m.state = 'active'
        and capacity = 'editor'
        and u.state = 'active'
        and m.group_id = :ckan_user_org_id;
    """
    return generar_csv_desde_sql(sql,ckan_user_org_id)


def generar_csv_peticiones_datos_por_estado(ckan_user_org_id):
    sql = text("""
    select
        DATE_FORMAT(NOW(), '%Y-%m-%d') as date, d.name as state, count(*) as value
    from
        node_field_data n
    inner join node__field_organismo_responsable org on n.nid = org.entity_id 
    inner join taxonomy_term__field_ckan_organization_id tx on tx.entity_id = org.field_organismo_responsable_target_id 
    inner join node__field_estado nfe on
        n.nid = nfe.entity_id
    inner join taxonomy_term__field_estado_id ttfei on ttfei.entity_id = nfe.field_estado_target_id 
    inner join taxonomy_term_field_data d on d.tid = nfe.field_estado_target_id 
    where
        n.`type` like 'peticion_de_datos' and n.langcode = 'es'
        and n.status = 1 
        and d.langcode = 'es'
        and tx.field_ckan_organization_id_value = :ckan_user_org_id
    group by d.name;
    """)
    return generar_csv_desde_mysql(sql,ckan_user_org_id)



def dge_load_json(value):
    """
    Return stored json representation as a dict, if
    value is already a dict just pass it through.
    """
    if isinstance(value, dict):
        return value
    if value is None:
        return {}
    try:
        return json.loads(value)
    except ValueError:
        return {}

def dge_dump_json(value):
    """
    Return a list or dict as json
    """
    return json.dumps(value)

def dge_field_display_subfields(field_name, schema_fields):
    """
    :param field_name: field name
    :param schema_fields:  fields of dataset or resource

    Return a dictionary with subfield names and
    values for field_name in scheme. None if field not exists in scheme
    """
    subfields_dict = {}
    if field_name and schema_fields:
        for field in schema_fields:
            if field and field['field_name'] and field['field_name'] == field_name:
                for subfield in field['repeating_subfields']:
                    if subfield:
                        subfields_dict[subfield['field_name']] = subfield
    return subfields_dict

def dge_get_telephone_from_iri(telephone_iri):
    '''
    :param telephone_iri: Telephone IRI
    
    Return a str with the telephone value
    '''
    telephone_str = ''
    if telephone_iri and telephone_iri.startswith('tel:'):
        telephone_str = telephone_iri[len('tel:'):]
    return telephone_str

def dge_get_email_from_iri(email_iri):
    '''
    :param email_iri: Email IRI
    
    Return a str with the email value
    '''
    email_str = ''
    if email_iri and email_iri.startswith('mailto:'):
        email_str = email_iri[len('mailto:'):]
    return email_str

def dge_is_dcatapes(pkg_dict):
    '''
    :param pkg_dict: Package dict
    
    Return True if application profile is dcatapes. False otherwise
    '''
    if pkg_dict:
        extras = pkg_dict['extras'] if ('extras' in pkg_dict and pkg_dict['extras']) else None
        if extras:
            for extra in extras:
                if extra['key'] == constants.KEY_EXTRA_DATASET_APPLICATION_PROFILE:
                    return True if extra['value'] == constants.VALUE_APPLICATION_PROFILE_DCATAPES else False
    return False

def dge_is_hvd(pkg_dict):
    '''
    :param pkg_dict: dataset dict
    
    Return True if dataset is HVD. False otherwise
    '''
    if pkg_dict:
        extras = pkg_dict['extras'] if ('extras' in pkg_dict and pkg_dict['extras']) else None
        if extras:
            for extra in extras:
                if extra['key'] == constants.KEY_EXTRA_DATASET_HVD:
                    return json.loads(extra['value'])
    return False

def dge_get_format_from_vocabulary_uri(format_value):
    '''
    :param format_value: Format value (URI or id)
    
    Return the format label
    for dcat:packageFormat, dcat:compressFormat, dcat:mediaType and dct:format.
    Also True if format_value is IANA / European URI, False otherwise    
    '''
    format_str = ''
    if format_value:
        if format_value.startswith(constants.DGE_IANA_FORMATS_PREFIXES):
            prefix = constants.DGE_IANA_FORMATS_PREFIX_HTTPS if format_value.startswith(constants.HTTPS_PREFIX) else constants.DGE_IANA_FORMATS_PREFIX_HTTP
            format_str = format_value[len(prefix):]
            return dge_resource_format_label(format_str), True
        if format_value.startswith(constants.EUROPEAN_PREFIX):
            format_str, xml_lang = dge_get_vocabularies_uri_label(format_value, 'en')
            return format_str, True
        return dge_resource_format_label(format_value), False
    return format_str

def dge_get_include_fields(entity_type):
    '''
    Return a list of resource fields
    '''
    if entity_type:
        if entity_type == 'dataset':
            return constants.DATASET_INCLUDE_FIELDS
        elif entity_type == 'resource':
            return constants.RESOURCE_INCLUDE_FIELDS
        elif entity_type == 'dataservice':
            return constants.DATASERVICE_INCLUDE_FIELDS
    return {}

def dge_is_datosgobes_spatial_uri(spatial_uri):
    '''
    :param spatial_uri: spatial uri
    
    Return True if spatial uri belongs to datosgob vocabulary.
    Return False otherwise
    '''
    if spatial_uri and spatial_uri.startswith(constants.SPATIAL_DATOSGOBES_PREFIX):
        return True
    return False

def dge_is_datosgobes_theme_uri(theme_uri):
    '''
    :param theme_uri: theme uri
    
    Return True if theme uri belongs to datosgob vocabulary.
    Return False otherwise
    '''
    if theme_uri and theme_uri.startswith(constants.THEME_DATOSGOBES_PREFIX):
        return True
    return False

def dge_count_resources(resources_lists):
    '''
    :param resources_list: list of resources
    
    Return the number of elements in the list
    '''
    count = 0
    if resources_lists:
        for resources_list in resources_lists:
            if resources_list:
                count += len(resources_list)
    return count

def dge_get_vocabularies_uri_label(uri, lang=None):
    '''
    :param uri: URI of term from vocabularies
    
    :param lang: language label
    
    Return the label for the URI in specified language, current language
    or default_locale if exists and default_locale for xml:lang property
    if needed or None otherwise. Return the URI otherwise
    '''
    label = uri
    xml_lang = None
    try:
        if not lang:
            lang = tkh.lang()
        default_locale = dge_default_locale()
        alternative_locale = config.get('ckan.locale_alternative_default', 'en')
        _label = None
        labels = dge_harvest_get_vocabulary_element_label_dict(uri)
        if labels:
            for language in [lang, default_locale, alternative_locale]:
                _label = labels.get(language, None)
                if _label:
                    xml_lang = language if language != lang else None
                    break
        if _label:
            label = _label.capitalize() if not _label.isupper() else _label
    except Exception as e:
        log.debug(f'Exception {type(e)} parsing vocabulary {uri}: {str(e)}')
    return label, xml_lang

def dge_get_served_by_dataservice(dataservices_uris):
    '''
    :param dataservices_uris: served_by_dataservice extra in dataset dict
    
    Return a list of dictionaries with dataservices title and url. {} otherwise
    '''
    dataservices_list = []
    catalog_uris = _dge_get_catalog_uris()
    if dataservices_uris:
        for dataservice_uri in dataservices_uris:
            dataservice_dict = dge_display_dataservice_data(dataservice_uri, catalog_uris)
            if dataservice_dict:
                dataservices_list.append(dataservice_dict)
        sorted_dataservices = sorted(dataservices_list, key=itemgetter('title'), reverse=False)
    return sorted_dataservices

def dge_get_datasets_served_by_dataservice(dataservice_id):
    '''
    :param dataservice_id: Dataservice id
    
    Return a sorted list of all datasets served by the dataservice in the view.
    '''
    sorted_datasets = []
    if dataservice_id:
        dataservice_uri = model.Session.query(model.PackageExtra.value)\
                        .filter_by(key='ckan_uri')\
                        .filter_by(package_id=dataservice_id)\
                        .scalar()
        if dataservice_uri:
            datasets_ids = []
            query = '''
                    select pe.package_id
                    from public.package_extra pe
                    where pe.key = 'served_by_dataservice'
                    and '{p0}' = any (select json_array_elements_text(pe.value::json));
                    '''.format(p0=dataservice_uri)
            datasets_ids = [item[0] for item in model.Session.execute(query).fetchall()]
            if datasets_ids:
                datasets_info = model.Session.query(model.Package.title, model.Package.name)\
                                .filter(model.Package.id.in_(datasets_ids))\
                                .all()
                if datasets_info:
                    datasets_list = []
                    for dataset_info in datasets_info:
                        dataset_dict = {}
                        dataset_dict['title'] = dataset_info[0]
                        dataset_dict['name'] = dataset_info[1]
                        datasets_list.append(dataset_dict)
                    sorted_datasets = sorted(datasets_list, key=itemgetter('title'), reverse=False)
    return sorted_datasets

def dge_count_served_by_dataservice(dataservices_list):
    '''
    :param dataservices_list: Dataservices list
    
    Return number of dataservices which serve the dataset
    '''
    return len(dataservices_list) if dataservices_list else 0

def dge_has_resource_identification_info(resource, res_dict_fields, is_dcatapes):
    '''
    :param resource: resource dict
    :param res_dict_fields: schema resource fields dict
    :param is_dcatapes: Whether the resource is dcatapes or not
    
    Return True if there is, at least, value for one of the
    identification info fields. Return False otherwise
    '''
    for item in resource:
        if not is_dcatapes and item == 'resource_identifier' and resource[item] and res_dict_fields[item]:
            return True
        if item in constants.RESOURCE_IDENTIFICATION_INFO_FIELDS and resource[item] and res_dict_fields[item]:
            return True
    return False

def dge_has_resource_interoperability_info(resource, res_dict_fields, is_dcatapes):
    '''
    :param resource: resource dict
    :param res_dict_fields: schema resource fields dict
    
    Return True if there is, at least, value for one of the
    interoperatbility info fields. Return False otherwise
    
    '''
    for item in resource:
        if is_dcatapes and item == 'media_type' and resource[item] and res_dict_fields[item]:
            return True
        if item in constants.RESOURCE_INTEROPERABILITY_INFO_FIELDS and resource[item] and res_dict_fields[item]:
            return True
    return False

def dge_has_resource_provenance_info(resource, res_dict_fields):
    '''
    :param resource: resource dict
    :param res_dict_fields: schema resource fields dict
    
    Return True if there is, at least, value for one of the
    provenance info fields. Return False otherwise
    
    '''
    for item in resource:
        if item in constants.RESOURCE_PROVENANCE_INFO_FIELDS and resource[item] and res_dict_fields[item]:
            return True
    return False

def dge_has_resource_reusability_info(resource, res_dict_fields, is_dcatapes):
    '''
    :param resource: resource dict
    :param res_dict_fields: schema resource fields dict
    :param is_dcatapes: Whether the resource is dcatapes or not
    
    Return True if there is, at least, value for one of the
    reusability info fields. Return False otherwise
    
    '''
    for item in resource:
        if not is_dcatapes and item == 'resource_relation' and resource[item] and res_dict_fields[item]:
            return True
        if is_dcatapes and item == 'resource_license' and resource[item] and res_dict_fields[item]:
            return True
        if item in constants.RESOURCE_REUSABILITY_INFO_FIELDS and resource[item] and res_dict_fields[item]:
            return True
    return False

def dge_has_package_information_info(package_dict, dict_fields, is_dcatapes, package_type):
    '''
    :param package_dict: package dict
    :param dict_fields: schema package fields dict
    :param is_dcatapes: Whether the package is dcatapes or not
    :param package_type: Type of package (dataset or dataservice)
    
    Return True if there is, at least, value for one of the
    information info fields. Return False otherwise
    '''
    package_fields = constants.DATASET_INFORMATION_INFO_FIELDS if package_type == 'dataset' else constants.DATASERVICE_INFORMATION_INFO_FIELDS
    for item in package_dict:
        if not is_dcatapes and package_type == 'dataset' and item == 'valid' and package_dict[item] and dict_fields[item]:
            return True
        if item in package_fields and package_dict[item] and dict_fields[item]:
            return True
    return False

def dge_has_dataset_technical_sheet_info(dataset_dict, dict_fields, is_dcatapes):
    '''
    :param dataset_dict: dataset dict
    :param dict_fields: schema dataset fields dict
    :param is_dcatapes: Whether the dataset is dcatapes or not
    
    Return True if there is, at least, value for one of the
    technical sheet info fields. Return False otherwise
    '''
    for item in dataset_dict:
        if not is_dcatapes and item == 'reference' and dataset_dict[item] and dict_fields[item]:
            return True
        if item in constants.DATASET_TECHNICAL_SHEET_INFO_FIELDS and dataset_dict[item] and dict_fields[item]:
            return True
    return False

def dge_has_package_contact_info(package_dict, dict_fields, package_type):
    '''
    :param package_dict: package dict
    :param dict_fields: schema package fields dict
    :param package_type: Type of package (dataset or dataservice)
    
    Return True if there is, at least, value for one of the
    contact info fields. Return False otherwise
    '''
    package_fields = constants.DATASET_CONTACT_INFO_FIELDS if package_type == 'dataset' else constants.DATASERVICE_CONTACT_INFO_FIELDS
    for item in package_dict:
        if item in package_fields and package_dict[item] and dict_fields[item]:
            return True
    return False

def dge_has_package_quality_info(package_dict, dict_fields, package_type):
    '''
    :param package_dict: package dict
    :param dict_fields: schema package fields dict
    :param package_type: Type of package (dataset or dataservice)
    
    Return True if there is, at least, value for one of the
    quality info fields. Return False otherwise
    '''
    package_fields = constants.DATASET_QUALITY_INFO_FIELDS if package_type == 'dataset' else constants.DATASERVICE_QUALITY_INFO_FIELDS
    for item in package_dict:
        if item in package_fields and package_dict[item] and dict_fields[item]:
            return True
    return False

def dge_get_count_active_package(package_type, search_query=None, org_id=None):
    '''
    :param package_type: Package type
    :param search_query: Optional search query for filtering the results.
    Return the number of active package_type entities in the catalog
    that the user can access. If search_query is provided, it will
    filter based on that query.
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user, 'auth_user_obj': c.userobj}

    fq = '+dataset_type:' + package_type + ' +state:(draft OR active)'
    if org_id:
        fq = fq + ' +owner_org:(' + org_id + ')'
    data_dict = {
        'q': search_query if search_query else '',
        'fq': fq,
        'include_private': True
    }

    result = logic.get_action('package_search')(context, data_dict)
    return result['count'] if result and 'count' in result else 0

def dge_get_search_package_count(package_type, search_query=None, org_id=None):
    '''
    :param package_type: Package type
    :param search_query: Optional search query for filtering the results.
    Return the number of active package_type entities in the catalog
    that the user can access. If search_query is provided, it will
    filter based on that query.
    '''
    context = {'model': model, 'session': model.Session,
               'user': c.user, 'auth_user_obj': c.userobj}

    fq = ''
    search_extras = {}
    for (param, value) in request.params.items(multi=True):
        if param not in ['q', 'page', 'sort', FACET_OPERATOR_PARAM_NAME] \
                and len(value) and not param.startswith('_'):
            if not param.startswith('ext_'):
                c.fields.append((param, value))
                fq += '%s:"%s" ' % (param, value)
            else:
                search_extras[param] = value

    # set allowed facets by type of package
    allowed_facets = DATASET_ALLOWED_FACETS if package_type == 'dataset' else DATASERVICE_ALLOWED_FACETS

    fq = fq + '+dataset_type:' + package_type + ' +state:(draft OR active)'
    if org_id:
        fq = fq + ' +owner_org:(' + org_id + ')'

    data_dict = {
        'q': search_query if search_query else '',
        'fq': fq,
        'extras': search_extras,
        'facet': False,
        'facet.field': allowed_facets,
        'rows': 0,
        'include_private': True
    } 

    result = logic.get_action('package_search')(context, data_dict)
    return result['count'] if result and 'count' in result else 0

def dge_has_guid(package_dict):
    '''
    :param package_dict: package dict
    
    Return True if package has guid. False otherwise
    '''
    if package_dict:
        extras = package_dict['extras'] if ('extras' in package_dict and package_dict['extras']) else None
        if extras:
            for extra in extras:
                if extra['key'] == constants.KEY_EXTRA_DATASET_GUID:
                    return True
    return False

def dge_is_editable(package_dict):
    '''
    :param package_dict: Package dict
    
    Return True if the package could be editable, False otherwise
    '''
    if package_dict:
        return False if dge_is_dcatapes(package_dict) else True
    return False

def dge_get_nti_field_uri_label(field, value):
    '''
    :param field: Metadata field
    :param value: Current value of metadata field
    
    return label for value and field if exists. False otherwise
    '''
    if field and value:
        for choice in dsh.dge_get_nti_field_choices(field):
            if choice['value'] == value:
                return choice['label']
    return False

def dge_get_request_params_for_text_search(request_params, facet_titles):
    '''
    :param request_params: Request params
    :param facet_titles: Facet titles
    
    Return a dict with each key and its values from the request params
    or {} if there are none
    '''
    if not request_params or not facet_titles:
        return {}
    request_params_dict = {}
    facet_operator_values = request_params.getlist('_facet_operator') if '_facet_operator' in request_params else []
    if facet_operator_values:
        request_params_dict['_facet_operator'] = facet_operator_values if isinstance(facet_operator_values, list) else [facet_operator_values]
    for facet_title in facet_titles:
        param_values = request_params.getlist(facet_title) if facet_title in request_params else []
        if param_values:
            request_params_dict[facet_title] = param_values if isinstance(param_values, list) else [param_values]
    return request_params_dict

def dge_url_for_broken_links():
    ''' Returns the Broken links url to the Organization in which the user active is editor '''
    if getattr(g, u'user', None):
        if c.userobj.sysadmin:
            return '/report/broken-links'
        else:
            orgs = get_action('organization_list_for_user')(data_dict={'permission': 'read'})
            if orgs and len(orgs) > 0:
                return f'/report/broken-links?organization={orgs[0].get("name")}'
    return None

def dge_get_display_byte_size(byte_size):
    value = f"{byte_size} {_('Bytes')}"
    try:
        _bytes = int(byte_size)
        mb = 1024*1024
        kb = 1024
        if _bytes >=  mb:
            value =  f"{round(_bytes/mb, 2)} {_('MB')}"
        elif _bytes >= kb :
            value =  f"{round(_bytes/kb, 2)} {_('KB')}"
    except ValueError:
        pass
    return value

def dge_display_dataservice_data(dataservice_uri, catalogs_uris=None):
    '''
    Set title and uri to show
    '''
    _catalog_uris = catalogs_uris or _dge_get_catalog_uris()
    dataservice_dict = {}
    if dataservice_uri and dataservice_uri.startswith(tuple(_catalog_uris)):
        dataservice_name = dataservice_uri.rsplit('/', 1)[-1]
        result = model.Session.query(model.Package)\
                      .filter_by(name=dataservice_name)\
                      .filter_by(type='dataservice')\
                      .filter_by(state='active')\
                      .filter_by(private=False)\
                      .first()
        if result:
            dataservice_dict['title'] = result.title
            dataservice_dict['uri'] =  h.url_for('package.dataset_read', id=result.name, qualified = True)
        else:
            dataservice_dict['title'] = dataservice_uri
            dataservice_dict['uri'] = dataservice_uri
    return dataservice_dict

def _dge_get_catalog_uris():
    catalog_uris = []
    base_uri = config.get('ckanext.dcat.base_uri', None)
    site_uri = config.get('ckan.site_url', None)
    if base_uri:
        catalog_uris.append(base_uri)
    if site_uri:
        catalog_uris.append(site_uri)
    return catalog_uris