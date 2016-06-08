import cgi
import pylons.config as config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
import requests
import tempfile
from PIL import Image
from PIL import PngImagePlugin, JpegImagePlugin
from StringIO import StringIO


def thumbnail_url(package_id):
    '''Returns the url of a thumbnail for a dataset. 

    Looks for a resource "thumbnail.png" in a dataset.
    Will generate a thumbnail and save it to the dataset if there isn't one already.

    To change this setting add to the
    [app:main] section of your CKAN config file::

      ckan.datasetthumbnail.show_thumbnail = true

    :rtype: string
    '''

    cfg_show = config.get('ckan.datasetthumbnail.show_thumbnail', False)
    show_thumbnail = toolkit.asbool(cfg_show)

    if not show_thumbnail:
        return None

    if package_id == None or len(package_id) == 0:
        return '/image-icon.png'

    cfg_width = config.get('ckan.datasetthumbnail.thumbnail_width', 140)
    thumbnail_width = toolkit.asint(cfg_width)
    cfg_height = config.get('ckan.datasetthumbnail.thumbnail_height', int(thumbnail_width * 1.415))
    thumbnail_height = toolkit.asint(cfg_height)

    package = toolkit.get_action('package_show')(data_dict={'id': package_id})

    for resource in package['resources']:
        if resource['name'] == "thumbnail.png":
            return resource['url']

    #if there's no thumbnail make one and add it to the dataset

    for resource in package['resources']:
        if resource['format'] == 'JPEG':

            response = requests.get(resource['url'], stream=True)
            if response.status_code == 200:
                original_fp = StringIO()  #create an in-memory file object in which to save the image

                for chunk in response.iter_content(1024):
                    original_fp.write(chunk)
                original_fp.flush()

                image = Image.open(original_fp)
                image.thumbnail((thumbnail_width, thumbnail_height))

                thumbnail_fp = StringIO() 
                thumbnail_fp.name = 'thumbnail.png'
                image.save(thumbnail_fp, format='PNG')

                thumbnail_resource = {}
                thumbnail_resource['package_id'] = package['id']
                thumbnail_resource['url'] = 'thumbnail.png'
                thumbnail_resource['url_type'] = 'upload'
                thumbnail_resource['format'] = 'png'
                thumbnail_resource['name'] = 'thumbnail.png'
                thumbnail_resource['upload'] = _UploadLocalFileStorage(thumbnail_fp)

                created_resource = toolkit.get_action('resource_create')(data_dict=thumbnail_resource)
                thumbnail_fp.close()
                original_fp.close()

                return created_resource['url']

    return '/image-icon.png'


class _UploadLocalFileStorage(cgi.FieldStorage):
    def __init__(self, fp, *args, **kwargs):
        self.name = fp.name
        self.filename = fp.name
        self.file = fp



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
