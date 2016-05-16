import logging
import collections

import ckan.plugins as plugins
import ckan.plugins.toolkit as tk


def create_gov_types():
    '''Create gov_types vocab and tags, if they don't exist already.'''
    user = tk.get_action('get_site_user')({'ignore_auth': True}, {})
    context = {'user': user['name']}
    try:
        data = {'id': 'gov_types'}
        tk.get_action('vocabulary_show')(context, data)
        logging.info("Example genre vocabulary already exists, skipping.")
    except tk.ObjectNotFound:
        logging.info("Creating vocab 'gov_types'")
        data = {'name': 'gov_types'}
        vocab = tk.get_action('vocabulary_create')(context, data)
        for tag in (u'Federal', u'Estatal', u'Municipal', u'Autonomo'):
            logging.info(
                    "Adding tag {0} to vocab 'gov_types'".format(tag))
            data = {'name': tag, 'vocabulary_id': vocab['id']}
            tk.get_action('tag_create')(context, data)


def gov_types():
    '''Return the list of government types from vocabulary.'''
    create_gov_types()
    try:
        gov_types = tk.get_action('tag_list')(
                data_dict={'vocabulary_id': 'gov_types'})
        return gov_types
    except tk.ObjectNotFound:
        return None


class GovLevelVocabPlugin(plugins.SingletonPlugin, tk.DefaultDatasetForm):
    '''Uses a tag vocabulary to add a custom metadata field to datasets.'''
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.IDatasetForm)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IFacets)

    # These record how many times methods that this plugin's methods are
    # called, for testing purposes.
    num_times_new_template_called = 0
    num_times_read_template_called = 0
    num_times_edit_template_called = 0
    num_times_search_template_called = 0
    num_times_history_template_called = 0
    num_times_package_form_called = 0
    num_times_check_data_dict_called = 0
    num_times_setup_template_variables_called = 0

    def update_config(self, config):
        # Add this plugin's templates dir to CKAN's extra_template_paths, so
        # that CKAN will use this plugin's custom templates.
        tk.add_template_directory(config, 'templates')

    def get_helpers(self):
        return {'gov_types': gov_types}

    def is_fallback(self):
        # Return True to register this plugin as the default handler for
        # package types not handled by any other IDatasetForm plugin.
        return True

    def package_types(self):
        # This plugin doesn't handle any special package types, it just
        # registers itself as the default (above).
        return []

    def _modify_package_schema(self, schema):
        # Add our custom gov_type metadata field to the schema.
        schema.update({
                'gov_type': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_tags')('gov_types')]
                })
        # Add our custom_test metadata field to the schema, this one will use
        # convert_to_extras instead of convert_to_tags.
        schema.update({
                'custom_text': [tk.get_validator('ignore_missing'),
                    tk.get_converter('convert_to_extras')]
                })
        schema['resources'].update({
                'custom_resource_text': [tk.get_validator('ignore_missing')]
                })
        return schema

    def create_package_schema(self):
        schema = super(GovLevelVocabPlugin, self).create_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def update_package_schema(self):
        schema = super(GovLevelVocabPlugin, self).update_package_schema()
        schema = self._modify_package_schema(schema)
        return schema

    def show_package_schema(self):
        schema = super(GovLevelVocabPlugin, self).show_package_schema()

        # Don't show vocab tags mixed in with normal 'free' tags
        # (e.g. on dataset pages, or on the search page)
        schema['tags']['__extras'].append(tk.get_converter('free_tags_only'))

        # Add our custom gov_type metadata field to the schema.
        schema.update({
            'gov_type': [
                tk.get_converter('convert_from_tags')('gov_types'),
                tk.get_validator('ignore_missing')]
            })

        # Add our custom_text field to the dataset schema.
        schema.update({
            'custom_text': [tk.get_converter('convert_from_extras'),
                tk.get_validator('ignore_missing')]
            })
        schema['resources'].update({
                'custom_resource_text': [tk.get_validator('ignore_missing')]
                })

        return schema

    # These methods just record how many times they're called, for testing
    # purposes.
    # TODO: It might be better to test that custom templates returned by
    # these methods are actually used, not just that the methods get
    # called.

    def setup_template_variables(self, context, data_dict):
        GovLevelVocabPlugin.num_times_setup_template_variables_called += 1
        return super(GovLevelVocabPlugin, self).setup_template_variables(
                context, data_dict)

    def new_template(self):
        GovLevelVocabPlugin.num_times_new_template_called += 1
        return super(GovLevelVocabPlugin, self).new_template()

    def read_template(self):
        GovLevelVocabPlugin.num_times_read_template_called += 1
        return super(GovLevelVocabPlugin, self).read_template()

    def edit_template(self):
        GovLevelVocabPlugin.num_times_edit_template_called += 1
        return super(GovLevelVocabPlugin, self).edit_template()

    def search_template(self):
        GovLevelVocabPlugin.num_times_search_template_called += 1
        return super(GovLevelVocabPlugin, self).search_template()

    def history_template(self):
        GovLevelVocabPlugin.num_times_history_template_called += 1
        return super(GovLevelVocabPlugin, self).history_template()

    def package_form(self):
        GovLevelVocabPlugin.num_times_package_form_called += 1
        return super(GovLevelVocabPlugin, self).package_form()

    # check_data_dict() is deprecated, this method is only here to test that
    # legacy support for the deprecated method works.
    def check_data_dict(self, data_dict, schema=None):
        GovLevelVocabPlugin.num_times_check_data_dict_called += 1

    # IPackageController
    def before_index(self, gov_type):
        tags = gov_type.get('tags', [])
        tags.extend(tag for tag in split_tags(gov_type.get('extras_tags', '')))
        gov_type['tags'] = tags

        org_name = gov_type['organization']
        group = model.Group.get(org_name)
        if group and ('gov_type' in group.extras):
            gov_type['gov_type'] = group.extras['gov_type']

        title_string = gov_type.get('title_string')
        if title_string:
            gov_type['title_string'] = title_string.strip().lower()

        cats = {}
        for extra in gov_type:
            if extra.startswith('__category_tag_'):
                cat = gov_type[extra]
                if cat:
                    try:
                        cat_list = json.loads(cat)
                        cats['vocab_%' % extra] = cat_list
                        new_list = cats.get('vocab_category_all', [])
                        new_list.extend(cat_list)
                        cats['vocab_category_all'] = new_list
                    except ValueError:
                        pass
        gov_type.update(cats)
        
        return gov_type
    
    
    # IFacets functions
    def dataset_facets(self, facets_dict, package_type):
        ##facets_dict['vocab_gov_types'] = 'Nivel de Gobierno'
        gov_facets = facets_dict
        facets_dict = collections.OrderedDict()
        facets_dict['theme'] = tk._('Categorias')
        facets_dict['vocab_gov_types'] = tk._('Nivel de Gobierno')
        for key in gov_facets.keys():
            facets_dict[key] = gov_facets[key]

        return facets_dict

    def group_facets(self, facets_dict, group_type, package_type):
        gov_facets = facets_dict
        facets_dict = collections.OrderedDict()
        facets_dict['vocab_gov_type'] = tk._('Nivel de Gobierno')
        for key in gov_facets.keys():
            facets_dict[key] = gov_facets[key]
        return facets_dict
        facets_dict.update({
                'vocab_gov_types': tk._('Nivel de Gobierno'),
                })
        return facets_dict

    def organization_facets(self, facets_dict, organization_type, package_type):
        gov_facets = facets_dict
        facets_dict = collections.OrderedDict()
        facets_dict['vocab_gov_type'] = tk._('Nivel de Gobierno')
        for key in gov_facets.keys():
            facets_dict[key] = gov_facets[key]
        return facets_dict
        facets_dict.update({
                'vocab_gov_types': tk._('Nivel de Gobierno'),
                })
        return facets_dict

