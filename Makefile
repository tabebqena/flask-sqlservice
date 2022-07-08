build:
	python3 -m build

check:
	twine check dist/*

test_upload:
	twine upload -r testpypi dist/*

upload:
	twine upload dist/*