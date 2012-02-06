# don't define urls here.  Do it either globally or by app
urlpatterns = patterns('',
    url(r'^(?P<app_model>\w+\.\w+)/(?P<field>\w+)/(?P<id>\d+)/$', 'uploadit.views.upload', name='uploadit'),
)
