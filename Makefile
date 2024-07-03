# Minimal makefile for Sphinx documentation
#
# Used only in linux systems

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
# adapted sphinx build: use when blender is used and adapter to the path to blender installation
SPHINXBUILD   ?= blender --background --python docs/src/blender_sphinx.py --
# standard sphinx build: use when blender is not part of the tool chain
# SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = docs/src
BUILDDIR      = docs/build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
%: Makefile
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
