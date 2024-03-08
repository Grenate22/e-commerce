from rest_framework.response import Response
from rest_framework.serializers import Serializer


class JsonResponse(Response):
    def __init__(self, data=None, msg=None,
                 status=None,statuscode=None,
                 template_name=None, headers=None,
                 exception=False, content_type=None, **kwargs):
        super().__init__(None,status=statuscode)

        if isinstance(data, Serializer):
            msg = (
                'You passed a Serializer instance as data, but '
                'probably meant to pass serialized `.data` or '
                '`.error`. representation.'
            )
            raise AssertionError(msg)

        self.data = {'status': status, 'data': data, 'message': msg}
        self.data.update(kwargs)

        self.data = {'status': status,"statuscode":statuscode, 'message': msg,'data': data}
        self.data.update(kwargs)
        self.template_name = template_name
        self.exception = exception
        self.content_type = content_type

        if headers:
            for name, value in headers.items():
                self[name] = value