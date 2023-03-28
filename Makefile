TEX_SRC   := tex
YML_SRC   := yaml
YML_FILES := $(wildcard ${YML_SRC}/*.yaml)
DIST      := dist
TEX_DIST  := ${DIST}/latex
TEX_DISTS := ${TEX_DIST}/a.toplevel.tex \
	${TEX_DIST}/c.chapter-1.tex


.PHONY: all
all: directories pdf


.PHONY: directories
directories:
	@mkdir -p ${DIST}
	@mkdir -p ${TEX_DIST}


.PHONY: pdf
pdf: ${TEX_DISTS}
	@cp tex/*.tex ${TEX_DIST}
	@latexmk -pdfxe -cd -bibtex -shell-escape -silent -jobname="book" \
			 -pretex="" -use-make -usepretex $(TEX_DIST)/a.book.tex
	@mv ${TEX_DIST}/book.pdf ${DIST}


${TEX_DIST}/%.tex: ${YML_SRC}/%.yaml
	@echo "Building $@"
	@python tools/converter.py ${YML_SRC}/$*.yaml \
							   ${TEX_DIST}/$*.tex \
							   --writer latex


.PHONY: clean
clean:
	@rm -rf ${DIST}
