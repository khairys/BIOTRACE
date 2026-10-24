.PHONY: setup test test-slow build schemas demo dev precompute ref-build
setup test test-slow build schemas demo dev precompute ref-build:
	python scripts/project.py $@
