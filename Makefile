unit_tests:
	coverage run -m unittest discover ./test/unit -v

coverage_html: unit_tests
	coverage html

server: coverage_html
	cd coverage_html_report && python -m SimpleHTTPServer

