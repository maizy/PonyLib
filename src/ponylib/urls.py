# _*_ coding: utf-8 _*_

__license__         = "GPL3"
__copyright__       = "Copyright 2011 maizy.ru"
__author__          = "Nikita Kovaliov <nikita@maizy.ru>"

__version__         = "0.1"
__doc__             = ""


from django.conf.urls.defaults import include, url, patterns
from django.views.generic import RedirectView

# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^$', RedirectView.as_view(url='search/', permanent=False), name='index'),
)

urlpatterns += patterns('ponylib.view.search',
    url(r'^search/$', 'index', name='search'),
    url(r'^search/results/$', 'results', name='search-results'),
)

urlpatterns += patterns('ponylib.view.download',
    url(r'^download/fb2/(?P<book_id>\d{1,})/(?P<book_name>.+)$', 'fb2', name='download-fb2'),
)

urlpatterns += patterns('',
    url(r'^i18n/', include('django.conf.urls.i18n'), name='set-language'),
    url(r'^about/', 'ponylib.view.global.about', name='about'),
    url(r'^debug/', 'ponylib.view.global.debug', name='debug'),
)

#urlpatterns += patterns('',
#     (r'^admin/doc/', include('django.contrib.admindocs.urls')),
#     (r'^admin/', include(admin.site.urls)),
# )
