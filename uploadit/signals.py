import django.dispatch

upload_done = django.dispatch.Signal(providing_args=["app", "model", "field",
                                                                    "instance"])
