# assumes several environmental variables are set
# DB_NAME

install:
	pip install -r requirements.txt

install_dev:
	pip install -r requirements/dev.txt

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

go:
	python ./typeseam/scripts/pull_from_typeform.py

check:
	python ./typeseam/scripts/get_seamless_pdf.py