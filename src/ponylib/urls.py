# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


from django.conf.urls.defaults import include, url, patterns
from django.views.generic import RedirectView

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^$', RedirectView.as_view(url='search/', permanent=False)),
)

urlpatterns += patterns('ponylib.view.search',
    (r'^search/$', 'index'),
    (r'^search/results/$', 'results'),
)

#urlpatterns += patterns('',
#     (r'^admin/doc/', include('django.contrib.admindocs.urls')),
#     (r'^admin/', include(admin.site.urls)),
# )
