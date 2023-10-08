
download_dependencies:
	pip install -r requirements.txt

download_gitignore:
	wget https://raw.githubusercontent.com/nymath/dev_tools/main/template/.gitignore

upload_package:
	rm -rf ./dist
	python setup.py sdist bdist_wheel
	twine upload dist/*