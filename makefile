all:
	make WCDB2.zip

clean:
	rm -f WCDB2.log
	rm -f WCDB2.zip
	rm -f *.pyc
	rm -rf html

turnin-list:
	turnin --list eladlieb cs373pj4

turnin-submit: WCDB2.zip
	turnin --submit eladlieb cs373pj4 WCDB2.zip

turnin-verify:
	turnin --verify eladlieb cs373pj4

# add other .py files

WCDB2.html: WCDB2.py
	pydoc -w WCDB2

WCDB2.log:
	git log > WCDB2.log

# add other .html and .py files

WCDB2.zip: WCDB2.html WCDB2.log WCDB2.pdf WCDB2.py WCDB2.xml WCDB2.xsd.xml TestWCDB2.py
	zip -r WCDB2.zip  WCDB2.html WCDB2.log WCDB2.pdf WCDB2.py WCDB2.xml WCDB2.xsd.xml TestWCDB2.py
