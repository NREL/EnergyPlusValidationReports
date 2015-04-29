#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import template_engine_impl

print("ARGS: " + str(sys.argv))

engine = template_engine_impl.TemplateEngine(sys.argv[1], sys.argv[2], sys.argv[3], None, False)

for sheet in sys.argv[5:]:
    engine.load_sheet(sys.argv[4], sheet)







