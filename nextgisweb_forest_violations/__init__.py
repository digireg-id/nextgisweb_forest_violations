# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from nextgisweb.component import Component


class ForestViolationsComponent(Component):
    identity = 'forest_violations'

    def initialize(self):
        pass

    def setup_pyramid(self, config):
        from . import view  # NOQA
        view.setup_pyramid(self, config)


def pkginfo():
    return dict(components=dict(
        forest_violations="nextgisweb_forest_violations"))
