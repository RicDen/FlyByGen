import sys
try:
    from sphinx.cmd import build
    import sphinx_design
    import furo
    import myst_parser
except:
    import pip
    print(pip.main(['install', 'sphinx', 'sphinx_design', 'furo', 'myst-parser']))
    from sphinx.cmd import build

first_sphinx_arg = sys.argv.index('-M')
build.make_main(['killme'] + sys.argv[first_sphinx_arg+1:])
