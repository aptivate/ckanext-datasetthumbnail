import ckan.config.middleware
import pylons.config as config
import webtest

import ckan.tests.helpers as helpers


class FunctionalTestBaseClass(helpers.FunctionalTestBase):
    @classmethod
    def setup_class(cls):
        super(FunctionalTestBaseClass, cls).setup_class()
        _load_plugin('datasetthumbnail')
        cls.app = _get_test_app()


def _get_test_app():
    '''Return a webtest.TestApp for CKAN, with legacy templates disabled.

    For functional tests that need to request CKAN pages or post to the API.
    Unit tests shouldn't need this.

    '''
    config['ckan.legacy_templates'] = False
    app = ckan.config.middleware.make_app(config['global_conf'], **config)
    app = webtest.TestApp(app)
    return app


def _load_plugin(plugin):
    '''Add the given plugin to the ckan.plugins config setting.

    This is for functional tests that need the plugin to be loaded.
    Unit tests shouldn't need this.

    If the given plugin is already in the ckan.plugins setting, it won't be
    added a second time.

    :param plugin: the plugin to add, e.g. ``datastore``
    :type plugin: string

    '''
    plugins = set(config['ckan.plugins'].strip().split())
    plugins.add(plugin.strip())
    config['ckan.plugins'] = ' '.join(plugins)
