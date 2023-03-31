TEX_SRC   := tex
YML_SRC   := yaml
YML_FILES := $(wildcard ${YML_SRC}/*.yaml)
TEX_FILES := $(wildcard $(TEX_SRC)/*.tex)
DIST      := dist
TEX_DIST  := ${DIST}/latex
TEX_DISTS := $(foreach yml,$(YML_FILES),\
	$(patsubst yaml/%.yaml,${TEX_DIST}/%.tex,$(yml)))


.PHONY: all
all: clean directories pdf


.PHONY: directories
directories:
	@mkdir -p ${DIST}
	@mkdir -p ${TEX_DIST}


.PHONY: pdf
pdf: ${TEX_DISTS}
	@cp tex/*.tex ${TEX_DIST}
	@latexmk -pdfxe -cd -bibtex -shell-escape -jobname="book" \
			 -pretex="" -use-make -usepretex $(TEX_DIST)/a.book.tex
	@mv -v ${TEX_DIST}/book.pdf .


${TEX_DIST}/%.tex: ${YML_SRC}/%.yaml
	@echo "Building $@"
	@python tools/converter.py ${YML_SRC}/$*.yaml \
							   ${TEX_DIST}/$*.tex \
							   --writer latex


.PHONY: clean
clean:
	@rm -rf ${DIST}
	@rm -f book.pdf
