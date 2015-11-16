relateiq2postgres
=================
Sometimes you really need a database.

# Purpose

SalesforceIQ (formerly known as RelateIQ) offers the ability for users
to extend the schema. This is very convenient for users, but it is not
ideal for working with the data that gets created and updated. A
database (such as Postgres) would be useful.

# Installation

`git clone git@github.com:davejagoda/relateiq2postgres.git`

`cd relateiq2postgres`

`virtualenv venv`

`source venv/bin/activate`

`pip install -r requirements.txt`

# Mapping of types from Python to Postgres

|python |postgres|
|-------|--------|
|int    |bigint  |
|unicode|text    |

# Resources

https://api.salesforceiq.com

http://www.postgresql.org/docs/current/static/datatype.html
