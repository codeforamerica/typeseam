# assumes several environmental variables are set
# DB_NAME

install:
	pip install -r requirements.txt

install.dev:
	pip install -r requirements/dev.txt
	npm install

db.drop:
	rm -rf ./migrations
	dropdb $(DB_NAME)

db.create:
	createdb $(DB_NAME)

db.init:
	python manage.py db init
	python manage.py db migrate
	python manage.py db upgrade

db.rebuild:
	make db.drop
	make db.create
	make db.init

serve:
	gulp

test:
	export CONFIG='typeseam.settings.TestConfig'
	nosetests \
		--verbose \
		--nocapture \
		--with-coverage \
		--cover-package=./typeseam \
		--cover-erase