# typeseam

This is an alpha proof-of-concept software for tying together [Typeform](http://www.typeform.com/) forms and
[SeamlessDocs](http://www.seamlessdocs.com/) pdf forms, for the purpose of auto-filling pdfs from an ad-hoc webform.

It arose out of a need to more rapidly make webforms that can auto-fill pdf forms.

Here's the next steps:

- [x] connect and authenticate to both Typeform and SeamlessDocs APIs
- [x] create a mapped translation between a Typeform form and a SeamlessDocs pdf
- [x] create a post url for receiving typeform submissions and saving them
- [x] create a process for filling the pdf with typeform submissions
- [ ] deploy
- [ ] improve the UI
- [ ] create logins to protect the privacy of form submissions
- [ ] allow for adding more than one form
- [ ] use a simple task queue for external API calls

## Quickstart

1. Create a python virtual environment running Python 3 (this has not yet been tested with Python 2)
2. Clone this repo and activate your virtual environment
3. Set the required environmental variables (discussed below) using a method of your choice
4. create a PostgreSQL database that you can connect to with the `DATABASE_URI` environmental variable
5. run `make install`
6. run `make db.init`
7. run `make serve` to start the local server

## Environmental Variables

Since this is connecting to external APIs, it expects you to have some sensitive information available as command line environmental variables.

Here is an example `.env` file with a list of the necessary variables:

```
DB_NAME='typeseam'
DATABASE_URI="postgresql+psycopg2://bgolder@localhost/$DB_NAME"
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

