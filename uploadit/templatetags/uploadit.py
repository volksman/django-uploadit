from django import template
from django.conf import settings

register = template.Library()

class UploadItNode(template.Node):

    def __init__(self, app, model, field, id):
        self.app = app
        self.model = model
        self.field = field
        self.id = template.Variable(id)

    def render(self, context):
        try:
            id = self.id.resolve(context)
        except template.VariableDoesNotExist:
            return ''

        t = template.loader.select_template(['uploadit/%s_%s.html' % (self.app,
                                                                    self.model),
                                                        'uploadit/base.html'])

        c = template.Context({ 'STATIC_URL':settings.STATIC_URL,
                                'app_model': self.app + "." + self.model,
                                'model': self.model,
                                'app': self.app,
                                'field': self.field,
                                'id': id })

        return t.render(c)

@register.tag()
def uploadit_form(parser, token):
    try:
        tag_name, app_model, field, id = token.split_contents()
    except ValueError:
        raise template.TemplateSyntaxError('%r tag requires 3 args' % tag_name)

    if not (app_model[0] == app_model[-1] and app_model[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's app.model argument should be wrapped in quotes" % tag_name)

    if not (field[0] == field[-1] and field[0] in ('"', "'")):
        raise template.TemplateSyntaxError("%r tag's field argument should be wrapped in quotes" % tag_name)

    try:
        app, model = app_model.split('.')
    except:
        raise template.TemplateSyntaxError('%r requires first arg to be <app>.<model>' % token.contents.split()[0])

    return UploadItNode(app[1:], model[:-1], field[1:-1], id)
