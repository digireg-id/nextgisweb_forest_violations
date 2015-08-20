# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from __future__ import division

# Inspired by Mapnik Map::fixAspectRatio()
def fix_aspect_ratio(e, s):
    e = list(e)
    ew, eh = e[2] - e[0], e[3] - e[1]
    sw, sh = s[0], s[1]

    er = ew / eh
    sr = sw / sh

    if er == sr:
        return e

    if er > sr:
        dh = (ew / sr - eh) / 2
        e[1] -= dh
        e[3] += dh
    else:
        dw = (eh * sr - ew) / 2
        e[0] -= dw
        e[2] += dw

    return e

def scale_extent(e, scale):
    e = list(e)
    ew, eh = e[2] - e[0], e[3] - e[1]

    ew_scaled = scale * ew
    eh_scaled = scale * eh

    ymin = (e[0] + e[2] - ew_scaled) / 2
    ymax = (e[0] + e[2] + ew_scaled) / 2
    xmin = (e[1] + e[3] - eh_scaled) / 2
    xmax = (e[1] + e[3] + eh_scaled) / 2

    return ymin, xmin, ymax, xmax
