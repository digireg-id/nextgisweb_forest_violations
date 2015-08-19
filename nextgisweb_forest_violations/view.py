# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from bunch import Bunch
from pyramid.response import Response

from nextgisweb.resource import DataScope
from nextgisweb.vector_layer import VectorLayer
from nextgisweb.feature_layer.api import serialize as wkt_serialize

DOCUMENTS = (
    ('docs', 'Документы'),
    ('sheet', 'Ведомости пересчета'),
    ('production', 'Лесопродукция'),
    ('vehicles', 'Техника'),
)

PERM_READ = DataScope.read
PERM_WRITE = DataScope.write


def serialize(feat):
    """Сериализация объекта, геометрия в GeoJSON
    """

    sfeat = wkt_serialize(feat)
    sfeat['geom'] = feat.geom.__geo_interface__
    return sfeat


def getdoc(context, request):
    """Возвращаем документ и связанные данные
    """

    p_srs = request.params.get('srs')
    p_traversal = request.params.get('traversal')

    fid = request.matchdict.get('fid')
    if fid is None: return None

    # Запрашиваемая система координат
    srsid = int(p_srs) if p_srs else 4326
    srs = Bunch(id=srsid)

    # Нужен ли рекурсивный обход
    traversal = int(p_traversal) if p_traversal else 1

    def traverse(id):
        resource = VectorLayer.filter_by(keyname='docs').one()
        request.resource_permission(PERM_READ, resource)

        query = resource.feature_query()
        query.filter_by(id=id)
        query.limit(1)
        query.srs(srs)
        query.geom()

        for doc in query():
            result = serialize(doc)

            result['related'] = {}
            for key, name in DOCUMENTS:
                result['related'][key] = []

                resource = VectorLayer.filter_by(keyname=key).one()
                request.resource_permission(PERM_READ, resource)

                query = resource.feature_query()
                query.filter_by(doc_id=doc.id)
                query.srs(srs)
                query.geom()

                for reldoc in query():
                    if key == 'docs' and traversal:
                        result['related'][key].append(traverse(reldoc.id))
                    else:
                        result['related'][key].append(serialize(reldoc))

        return result

    # Определяем связанные документы
    result = traverse(fid)

    return Response(
        json.dumps(result),
        content_type=b'application/json')


def setup_pyramid(comp, config):
    config.add_route('fv.doc', '/fvapi/document/{fid}')
    config.add_view(getdoc, route_name='fv.doc', request_method='GET')
