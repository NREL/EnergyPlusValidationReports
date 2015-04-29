#!/usr/bin/python
# -*- coding: utf-8 -*-

import re
import sys
import template_engine_impl

engine = template_engine_impl.TemplateEngine(sys.argv[1], sys.argv[2], sys.argv[3], re.compile(".*ASHRAE 1052RP-ver4.*"))
engine.execute();







