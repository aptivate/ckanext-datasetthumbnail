import sys
import cgi
import pylons.config as config
import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from ckan.common import c
import requests
import tempfile
from PIL import Image
from PIL import PngImagePlugin, JpegImagePlugin
from StringIO import StringIO
import ckanext

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

    cfg_auto_generate = config.get('ckan.datasetthumbnail.auto_generate', False)
    auto_generate = toolkit.asbool(cfg_auto_generate)

    if not show_thumbnail:
        return None

    if package_id == None or len(package_id) == 0:
        return '/image-icon.png'

    package = toolkit.get_action('package_show')(data_dict={'id': package_id})

    for resource in package['resources']:
        if resource['name'] == 'thumbnail.png':
            return resource['url']

    #if there's no thumbnail then automatically generate one and add it to the dataset
    url = None

    if auto_generate:
        if c.user != None and len(c.user) > 0:
            url = create_thumbnail(package_id)

    return url or '/image-icon.png'


def create_thumbnail(package_id, resource_id=None, width=None, height=None):
    '''Creates a thumbnail in a dataset and returns its url

    :rtype: string
    '''
    if c.user == None or len(c.user) == 0:
        return None

    if width == None:
        cfg_width = config.get('ckan.datasetthumbnail.thumbnail_width', 140)
        width = toolkit.asint(cfg_width)

    if height == None:
        cfg_height = config.get('ckan.datasetthumbnail.thumbnail_height', int(width * 1.415))
        height = toolkit.asint(cfg_height)

    package = toolkit.get_action('package_show')(
        context={'ignore_auth': True}, 
        data_dict={'id': package_id})

    resource = None    
    if resource_id != None:
        resource = toolkit.get_action('resource_show')(
            context={'ignore_auth': True}, 
            data_dict={'id': resource_id})        

    if resource == None:
        for pkg_resource in package['resources']:
            if pkg_resource['format'] == 'JPEG' or pkg_resource['format'] == 'PNG':
                resource = pkg_resource
                break


    if resource != None:

        if resource['url_type'] == 'upload':

            auth_header = None
            if hasattr(c, 'userobj') and hasattr(c.userobj, 'apikey'):
                auth_header = {'Authorization': c.userobj.apikey}

            response = requests.get(resource['url'], headers=auth_header, stream=True)
        else:
            response = requests.get(resource['url'], stream=True)

        if response.status_code == 200:
            original_fp = StringIO()  #create an in-memory file object in which to save the image

            for chunk in response.iter_content(1024):
                original_fp.write(chunk)
            original_fp.flush()

            image = None

            try:
                image = Image.open(original_fp)
            except IOError:
                #if an image can't be parsed from the response...
                return None 

            image.thumbnail((width, height))

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

            created_resource = toolkit.get_action('resource_create')(context={'ignore_auth': True}, data_dict=thumbnail_resource)
            thumbnail_fp.close()
            original_fp.close()

            return created_resource['url']

    return None


class _UploadLocalFileStorage(cgi.FieldStorage):
    def __init__(self, fp, *args, **kwargs):
        self.name = fp.name
        self.filename = fp.name
        self.file = fp



class DatasetthumbnailPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IConfigurer)
    plugins.implements(plugins.ITemplateHelpers)
    plugins.implements(plugins.IActions)


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

    #IActions
    def get_actions(self):
        return {
            'create_thumbnail':
            ckanext.datasetthumbnail.plugin.create_thumbnail,
        }
