from django.http import HttpResponse, HttpResponseBadRequest
from django.core.files.uploadedfile import UploadedFile
from django.db.models.loading import get_model
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt

import logging
log = logging

@csrf_exempt
def multiuploader(request, model_string):
    """
    Main Multiuploader module.
    Parses data from jQuery plugin and makes database changes.
    """
    if request.method == 'POST':
        log.info('received POST to main multiuploader view')
        if request.FILES == None:
            return HttpResponseBadRequest('Must have files attached!')

        #getting file data for farther manipulations
        file = request.FILES[u'files[]']
        wrapped_file = UploadedFile(file)
        filename = wrapped_file.name
        file_size = wrapped_file.file.size
        log.info ('Got file: "%s"' % str(filename))
        log.info('Content type: "$s" % file.content_type')

        #writing file manually into model
        #because we don't need form of any type.
        model = get_model(*model_string.split('.'))
        image = model()
        image.image=file
        image.save()
        log.info('File saving done')

        #getting thumbnail url using sorl-thumbnail
        #if 'image' in file.content_type.lower():
            #im = get_thumbnail(image, "80x80", quality=50)
            #thumb_url = im.url
        #else:

        #settings imports
        #try:
            #file_delete_url = settings.MULTI_FILE_DELETE_URL+'/'
            #file_url = settings.MULTI_IMAGE_URL+'/'+image.key_data+'/'
        #except AttributeError:
            #file_delete_url = 'multi_delete/'
            #file_url = 'multi_image/'+image.key_data+'/'

        #generating json response array
        result = []
        result.append({"name":filename,
                       "size":file_size,
                       "delete_type":"POST",})
        response_data = simplejson.dumps(result)

        #checking for json data type
        #big thanks to Guy Shapiro
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'
        return HttpResponse(response_data, mimetype=mimetype)
    else: #GET
        return HttpResponseBadRequest()
