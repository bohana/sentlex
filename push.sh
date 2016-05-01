echo "Building"
rm dist/*gz
python setup.py sdist
pip install --upgrade --force-reinstall --no-deps dist/*gz

echo "Testing"
cd tests
python -m unittest discover -v -p "unit*.py"
