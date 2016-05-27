import pylons.config as config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit


def thumbnail_url():
    '''Returns the url of a thumbnail for a dataset. 

    Looks for a resource "thumbnail.png" in a dataset. 
    Will generate a thumbnail and save it to the dataset if there isn't one already. 

    To change this setting add to the
    [app:main] section of your CKAN config file::

      ckan.datasetthumbnail.show_thumbnail = true

    :rtype: string
    '''
    show_thumbnail = config.get('ckan.datasetthumbnail.show_thumbnail', False)
    if not show_thumbnail:
        return None

    return '/image-icon.png'





class DatasetthumbnailPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)


    # IConfigurer
    def update_config(self, config_):
        toolkit.add_template_directory(config_, 'templates')
        toolkit.add_public_directory(config_, 'public')
        toolkit.add_resource('fanstatic', 'datasetthumbnail')

    #ITemplateHelpers
    def get_helpers(self):
        return {
            'thumbnail_url': thumbnail_url
        }