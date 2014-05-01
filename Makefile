install:
	@echo 'Use python setup.py install instead'

dist:
	@python setup.py bdist

clean:
	@rm -rf *.egg-info
	@rm -rf dist
	@rm -rf build
	@rm -rf */__pycache__
	@find . -name '*.sw?' -delete
	@find . -name '*.py?' -delete
	@python setup.py clean

