#!/usr/bin/env python
# vim:fileencoding=utf-8
# License: GPL v3 Copyright: 2021, Kovid Goyal <kovid at kovidgoyal.net>


import ast

from calibre.srv.tests.base import SimpleTest
from calibre_extensions.fast_css_transform import parse_css_number, transform_properties


class TestTransform(SimpleTest):

    def test_number_parsing(self):
        for x in '.314 -.314 0.314 0 2 +2 -1 1e2 -3.14E+2 2e-2'.split():
            self.ae(parse_css_number(x), ast.literal_eval(x))
        self.ae(parse_css_number('2em'), 2)
        self.ae(parse_css_number('.3em'), 0.3)
        self.ae(parse_css_number('3x3'), 3)

    def test_basic_css_transforms(self):
        def d(src, expected, is_declaration=True, url_callback=None):
            self.ae(transform_properties(src, is_declaration=is_declaration, url_callback=url_callback), expected)

        def upper_case(val):
            return val.upper()

        def u(src, expected, is_declaration=True, url_callback=upper_case):
            return d(src, expected, url_callback=url_callback, is_declaration=is_declaration)

        def s(src, expected, url_callback=upper_case):
            return d(src, expected, url_callback=url_callback, is_declaration=False)

        s('@im/* c */port "x.y";', '@import "X.Y";')
        s('@import url("narrow.css") supports(display: flex) handheld and (max-width: 400px);',
          '@import url("NARROW.CSS") supports(display: flex) handheld and (max-width: 400px);')
        s('@import url( x.y);', '@import url("X.Y");')

        u('background: url(  te  st.gif  ) 12; src: url(x)', 'background: url("TE  ST.GIF") 12; src: url("X")')
        u('background: url(te/**/st.gif); xxx: url()', 'background: url("TEST.GIF"); xxx: url()')
        u(r'background: url(t\)est.gif)', 'background: url("T)EST.GIF")')
        u('a:url(  "( )" /**/ )', 'a:url("( )")')
        u('a:url(  "(/*)"  )', 'a:url(  "(/*)"  )', url_callback=lambda x: x)

        d(r'f\ont-s\69z\65 : 16\px', 'font-size: 1rem')
        d('font -size: 16px', 'font -size: 16px')
        d('font-/* */size: 1/*x*/6/**/p/**/x !important', 'font-size: 1rem !important')
        d('fOnt-size :16px', 'fOnt-size :1rem')
        d('font-size:2%', 'font-size:2%')
        d('font-size: 72pt; margin: /*here*/ 20px; font-size: 2in', 'font-size: 6rem; margin: /*here*/ 20px; font-size: 12rem')
        d(r'''font: "some 'name" 32px''', 'font: "some \'name" 2rem')
        d(r'''font: 'some "name' 32px''', 'font: \'some "name\' 2rem')
        d(r'''font: 'some \n ame' 32px''', 'font: "some n ame" 2rem')
        d('''font: 'some \\\nname' 32px''', 'font: "some name" 2rem')
        d('font: sans-serif 16px/3', 'font: sans-serif 1rem/3')
        d('font: sans-serif small/17', 'font: sans-serif 0.8rem/17')

        d('-epub-writing-mode: a; -web/* */kit-writing-mode: b; writing-mode: c', 'writing-mode: a; writing-mode: b; writing-mode: c')
        d('xxx:yyy', 'xxx:yyy')
