# coding=utf-8
__author__ = 'Anita Hapsari <anita@kartoza.com>'
__date__ = '15/04/19'

import json
import os
from django.http.response import HttpResponseBadRequest
from rest_framework.views import APIView, Response


class GetMigrationProgress(APIView):
    """API to get the progress of data migration for a user."""

    def get(self, request):
        username = request.GET.get('username', None)
        if username:
            pathname = \
                os.path.join(
                    '/home/web/media',
                    'data-migration-progress/{}.txt'.format(
                        username))
            found = os.path.exists(pathname)

            if not found:
                return HttpResponseBadRequest('Data not found.')

            with open(pathname) as json_file:
                data = json.load(json_file)
                return Response(data)
