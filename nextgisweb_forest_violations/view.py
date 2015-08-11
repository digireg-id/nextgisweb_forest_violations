# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from pyramid.response import Response

from nextgisweb.resource import DataScope
from nextgisweb.vector_layer import VectorLayer
from nextgisweb.feature_layer.api import serialize

DOCUMENTS_STACK = (
    ('docs', 'Документы'),
    ('sheet', 'Ведомости пересчета'),
    ('production', 'Лесопродукция'),
    ('territory', 'Территории нарушения'),
    ('vehicles', 'Техника'),
)

PERM_READ = DataScope.read
PERM_WRITE = DataScope.write


def getdoc(context, request):
    """Возвращаем документ и связанные данные
    """

    resource = VectorLayer.filter_by(keyname='docs').one()
    request.resource_permission(PERM_READ, resource)

    fid = request.matchdict.get('fid')
    if fid is None:
        return None

    query = resource.feature_query()
    query.geom()

    query.filter_by(id=fid)
    query.limit(1)

    result = None
    for f in query():
        result = serialize(f)
        result['related'] = {}
        for key, display_name in DOCUMENTS_STACK:
            result['related'][key] = []

            resource = VectorLayer.filter_by(keyname=key).one()
            request.resource_permission(PERM_READ, resource)
            
            query = resource.feature_query()
            query.geom()

            query.filter_by(doc_id=f.id)
            for feat in query():
                result['related'][key].append(serialize(feat))

    return Response(
        json.dumps(result),
        content_type=b'application/json')


def setup_pyramid(comp, config):
    config.add_route('fv.doc', '/fvapi/document/{fid}')
    config.add_view(getdoc, route_name='fv.doc', request_method='GET')
