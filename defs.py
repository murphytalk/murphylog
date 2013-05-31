# -*- coding: utf-8 -*-
import os.path

TEMPLATE_SUBDIR = "templates"

dir = os.path.dirname(__file__)
RESTRUCTUREDTEXT_FILTER_SETTINGS = {'file_insertion_enabled': 0,
                                    'raw_enabled': 0,
                                    '_disable_config': 1,
                                    'stylesheet_path': '%s/lib/html4css1.css' % dir,
                                    'template': '%s/lib/template.txt' % dir, }
