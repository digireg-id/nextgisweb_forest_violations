# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from bunch import Bunch
from PIL import Image
from StringIO import StringIO
from pyramid.response import Response

from nextgisweb.resource import DataScope
from nextgisweb.vector_layer import VectorLayer
from nextgisweb.feature_layer.api import serialize as wkt_serialize
from nextgisweb.style import IRenderableStyle

from .utils import (
    fix_aspect_ratio,
    scale_extent,
)

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


def getdoc(request):
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


def getschema(request):
    """Возвращаем схему участка лесонарушения
    """

    p_size = map(int, request.GET.get('size').split(','))

    fid = request.matchdict.get('fid')
    if fid is None: return None

    resource = VectorLayer.filter_by(keyname='docs').one()
    request.resource_permission(PERM_READ, resource)

    query = resource.feature_query()
    query.filter_by(id=fid)
    query.limit(1)
    query.geom()
    query.box()

    for doc in query():
        extent = fix_aspect_ratio(doc.box.bounds, p_size)
        extent = scale_extent(extent, 3)

        # cadastre - лесоделение
        # docs - территории лесонарушений
        resstyles = []
        for key in ('cadastre', 'docs'):
            resource = VectorLayer.filter_by(keyname=key).one()
            request.resource_permission(PERM_READ, resource)
            resstyle = filter(lambda r: IRenderableStyle.providedBy(r),
                resource.children)[0]
            resstyles.append(resstyle)

        img = None
        for style in resstyles:
            request.resource_permission(PERM_READ, style)

            # Отфильтровываем документы для отрисовки
            if style.feature_layer.keyname == 'docs':
                cond = {'id': fid}
            else:
                cond = None

            req = style.render_request(style.srs, cond)
            rimg = req.render_extent(extent, p_size)
            img = rimg if img is None else Image.alpha_composite(img, rimg)

        buf = StringIO()
        img.save(buf, 'png')
        buf.seek(0)

        return Response(body_file=buf, content_type=b'image/png')


def setup_pyramid(comp, config):
    config.add_route('fv.doc', '/fvapi/document/{fid}')
    config.add_route('fv.schema', '/fvapi/schema/{fid}')
    config.add_view(getdoc, route_name='fv.doc', request_method='GET')
    config.add_view(getschema, route_name='fv.schema', request_method='GET')
