# typeseam

## This repo is no longer in use

Please look at [codeforamerica/intake](https://github.com/codeforamerica/intake) if you want to see the current active version of this project.

[![Build Status](https://travis-ci.org/codeforamerica/typeseam.svg?branch=master)](https://travis-ci.org/codeforamerica/typeseam) [![Coverage Status](https://coveralls.io/repos/codeforamerica/typeseam/badge.svg?branch=master&service=github)](https://coveralls.io/github/codeforamerica/typeseam?branch=master)

This is an alpha proof-of-concept software for tying together [Typeform](http://www.typeform.com/) forms and
[SeamlessDocs](http://www.seamlessdocs.com/) pdf forms, for the purpose of auto-filling pdfs from an ad-hoc webform.

It arose out of a need to more rapidly make webforms that can auto-fill pdf forms.

## Next steps

### For v0.01 — [sufficient features for one forgiving user](https://github.com/codeforamerica/typeseam/issues?q=is%3Aopen+is%3Aissue+milestone%3Av0.01)

- Better tests and mocking
- UI for failing API calls
- Logins and registration
- Ability to delete or hide specific repsonses

### For v0.02 — [sufficient features for a small group of forgiving users](https://github.com/codeforamerica/typeseam/issues?q=is%3Aopen+is%3Aissue+milestone%3Av0.02)

- Remove hardcoded question configuration, create models for storing configurations
- Create a UI for adding forms and editing question configurations
- Put blocking tasks & API calls into background task queues
- Sufficient features for a motivated, tech-savvy non-programmer to add forms

## Quickstart for local development

1. Create a python virtual environment running Python 3 (this has not yet been tested with Python 2)
2. Clone this repo and activate your virtual environment
3. Set the required environmental variables (discussed below) using a method of your choice
4. create a PostgreSQL database that you can connect to with the `DATABASE_URI` environmental variable
5. Make sure you have `npm` and `gulp` installed
6. run `make install.dev` to install all dependencies
7. run `make db.init` to set up the database
8. run `make serve` to start the local server
9. run `make test` to run tests (use `make test.full` to include selenium tests)

## Environmental Variables

Since this is connecting to external APIs, it expects you to have some sensitive information available as command line environmental variables.

Here is an example `.env` file with a list of the necessary variables:

```
DB_NAME='typeseam'
DATABASE_URI="postgresql+psycopg2://dbusername@localhost/$DB_NAME"
TEST_DATABASE_URI="postgresql+psycopg2://dbusername@localhost/test_$DB_NAME"
SECRET_KEY='o0o0o0o0o0o0o0o0oo0o0o'
CONFIG=typeseam.settings.DevConfig
PYTHONPATH=".:$PYTHONPATH"
TYPEFORM_API_KEY='o0o0o0o0o0o0o0o0o0o0o0o0o0o0'
DEFAULT_TYPEFORM_KEY='o0o0oo0o'
DEFAULT_SEAMLESS_FORM_ID='0o0o0o0o0o0o0o0o'
SEAMLESS_DOCS_API_KEY='0o0o0o0o0o0o0o0o0o0o0o'
SEAMLESS_DOCS_API_SECRET='0o0o0o0o0o0o0o0o0o0o0o0o'
```

Two of the keys (`DEFAULT_TYPEFORM_KEY` and `DEFAULT_SEAMLESS_FORM_ID`)
 are derived from using Typeform and SeamlessDocs.

## Adding a new user for live testing

There is a script that allows you to add a new user and give them 20 randomly-generated responses.

    python typeseam/scripts/add_user_with_responses.py user@email.com password
