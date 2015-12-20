# typeseam

This is an alpha proof-of-concept software for tying together [Typeform](http://www.typeform.com/) forms and
[SeamlessDocs](http://www.seamlessdocs.com/) pdf forms, for the purpose of auto-filling pdfs from an ad-hoc webform.

It arose out of a need to more rapidly make webforms that can auto-fill pdf forms.

Here's the next steps:

- [x] connect and authenticate to both Typeform and SeamlessDocs APIs
- [ ] create a mapped translation between a Typeform form and a SeamlessDocs pdf
- [ ] create a post url for receiving typeform submissions and saving them
- [ ] create a process for filling the pdf with typeform submissions
- [ ] fill lots of pdfs
- [ ] improve the process of translating between the two types of forms

## Quickstart

1. Create a python virtual environment running Python 3 (this has not yet been tested with Python 2)
2. Clone this repo and activate your virtual environment
3. Set the environmental variables (discussed below) using a method of your choice
4. run `make install`

## Environmental Variables

Since this is connecting to external APIs, it expects you to have some sensitive information available as command line environmental variables.

Here is an example `.env` file with a list of the necessary variables:

```
DB_NAME='typeseam'
DATABASE_URI="postgresql+psycopg2://dbusername@localhost/$DB_NAME"
SECRET_KEY='somethingSuperSecret'
CONFIG=typeseam.settings.DevConfig
PYTHONPATH=".:$PYTHONPATH"
TYPEFORM_API_KEY='o0o0o0o0o0o0o0o0o0o0o0o0o0o0o0o0o'
SEAMLESS_DOCS_API_KEY='o0o0o0o0o0o0o0o0o'
SEAMLESS_DOCS_API_SECRET='o0o0o0o0o0o0o0o0o0o0o0o0o0o0o0o0o'
```
