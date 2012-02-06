from django.http import HttpResponse, HttpResponseBadRequest
from django.shortcuts import get_object_or_404
from django.core.files.uploadedfile import UploadedFile
from django.db.models.loading import get_model
from django.utils import simplejson
from django.views.decorators.csrf import csrf_exempt
from django.db.models import FileField, ImageField

from uploadit.forms import FileForm
from uploadit.signals import upload_done

try:
    from attachments.models import Attachment
except:
    Attachment = False

import logging
log = logging

def create_string_wrapper(my_string):
    strings = {}
    return strings.setdefault(my_string, object())

@csrf_exempt
def upload(request, app_model, field, id, form=FileForm):
    """
    Main Multiuploader module.
    Parses data from jQuery plugin and makes database changes.
    """
    if request.method == 'POST':
        if "application/json" in request.META['HTTP_ACCEPT_ENCODING']:
            mimetype = 'application/json'
        else:
            mimetype = 'text/plain'

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

        instance = form({ 'filename': filename, 'id': id })
        if not instance.is_valid():
            return HttpResponse(simplejson.dumps([{
                                        'error': instance.errors['__all__'],
                                        'name': filename,
                                        'size': file_size,
                                        }]), mimetype=mimetype)

        #writing file manually into model
        #because we don't need form of any type.
        model = get_model(*app_model.split('.'))
        field_info = model._meta.get_field_by_name(field)
        obj = get_object_or_404(model, pk=id)
        if not isinstance(field_info[0], FileField) or not isinstance(field_info[0], ImageField):
            if Attachment:
                """ if the field we are uploading to is not a FileField or
                ImageField it is a generic attachment """
                att = Attachment()
                att.file.save(filename, file, save=False)
                att.added_by = request.user
                att.save()
                setattr(obj, field, att)
            else:
                raise "Cannot attach file"
        else:
            setattr(obj, field, file)

        obj.save()
        log.info('File saving done')

        upload_done.send(sender=create_string_wrapper('uploadit'),
                        app=app_model.split('.')[0],
                        model=app_model.split('.')[1],
                        field=field, instance=obj,
                        filename=filename)

        #generating json response array
        result = []
        result.append({"name":filename,
                       "size":file_size,
                       "delete_type":"POST",})

        response_data = simplejson.dumps(result)

        return HttpResponse(response_data, mimetype=mimetype)

    else: #GET
        return HttpResponseBadRequest()
