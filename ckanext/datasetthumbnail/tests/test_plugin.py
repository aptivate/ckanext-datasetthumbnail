import nose.tools

import ckanext.datasetthumbnail.plugin as plugin
import ckanext.datasetthumbnail.tests.helpers as custom_helpers
import ckan.tests.helpers as helpers

assert_equals = nose.tools.assert_equals
assert_true = nose.tools.assert_true

class TestThumbnail(custom_helpers.FunctionalTestBaseClass):

    @helpers.change_config('ckan.datasetthumbnail.show_thumbnail', False)
    def test_thumbnails_off(self):

        url = plugin.thumbnail_url(None)
        assert_equals(url, None)

    @helpers.change_config('ckan.datasetthumbnail.show_thumbnail', True)
    def test_no_valid_package_id(self):

        url = plugin.thumbnail_url(None)
        assert_equals(url, '/image-icon.png')

    @helpers.change_config('ckan.datasetthumbnail.show_thumbnail', True)
    def test_existing_thumbnail(self):
        pass

    @helpers.change_config('ckan.datasetthumbnail.show_thumbnail', True)
    def test_creating_thumbnail(self):
        pass
