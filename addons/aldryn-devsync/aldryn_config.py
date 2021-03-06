# -*- coding: utf-8 -*-
from functools import partial

from distutils.version import LooseVersion

from aldryn_client import forms


class Form(forms.BaseForm):
    enable_livereload = forms.CheckboxField(
        'Enable Livereload',
        required=False,
        initial=False,
        help_text='Auto reloads the website on changes made in local development.'
    )

    def to_settings(self, data, settings):
        import django
        from django.core.urlresolvers import reverse_lazy

        from aldryn_addons.utils import djsenv

        env = partial(djsenv, settings=settings)
        django_version = LooseVersion(django.get_version())

        cloud_sync_key = env('CMSCLOUD_SYNC_KEY')
        credential_url = env('LIVERELOAD_CREDENTIAL_URL')

        if django_version >= LooseVersion('1.8'):
            TEMPLATE_CONTEXT_PROCESSORS = settings['TEMPLATES'][0]['OPTIONS']['context_processors']
        else:
            TEMPLATE_CONTEXT_PROCESSORS = settings['TEMPLATE_CONTEXT_PROCESSORS']

        if 'aldryn_snake.template_api.template_processor' not in TEMPLATE_CONTEXT_PROCESSORS:
            TEMPLATE_CONTEXT_PROCESSORS.append('aldryn_snake.template_api.template_processor')

        if cloud_sync_key and credential_url:
            settings['LIVERELOAD_CREDENTIAL_URL'] = credential_url
            # By selectively adding the urls, we avoid having to do
            # all sorts of checks in the views, instead the views
            # have no logic as to what settings are required or not.
            settings['ADDON_URLS'].append('aldryn_devsync.urls')
            settings['INSTALLED_APPS'].append('aldryn_devsync')

        if 'ALDRYN_SSO_LOGIN_WHITE_LIST' in settings:
            # stage sso enabled
            # add internal endpoints that do not require authentication
            settings['ALDRYN_SSO_LOGIN_WHITE_LIST'].extend([
                reverse_lazy('devsync-add-file'),
                reverse_lazy('devsync-delete-file'),
                reverse_lazy('devsync-run-command'),
                reverse_lazy('livereload-iframe-content'),
                reverse_lazy('toggle-livereload'), #TODO: is ok for this to be white listed?
                reverse_lazy('devsync-trigger-sync'),
            ])

        settings['CMSCLOUD_SYNC_KEY'] = cloud_sync_key
        settings['LAST_BOILERPLATE_COMMIT'] = env('LAST_BOILERPLATE_COMMIT')
        settings['SYNC_CHANGED_FILES_URL'] = env('SYNC_CHANGED_FILES_URL')
        settings['SYNC_CHANGED_FILES_SIGNATURE_MAX_AGE'] = 60  # seconds

        settings['ALDRYN_DEVSYNC_ENABLE_LIVERELOAD'] = data['enable_livereload']
        return settings
