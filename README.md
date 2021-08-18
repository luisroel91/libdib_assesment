# libdib_assesment

To run this project you must have docker and docker-compose installed

This asynchronous API was made with:
* FastAPI
* SQLAlchemy (ORM)
* AuthJWT
* Pydantic
* Pandas
* PgAdmin
* Postgres
* Passlib

(The data that was provided is auto-loaded in bulk from a pickle on POST to /data/load_pickle but was pre-processed using Pandas,
you can see the script that was used to process data in the data_processing directory)

### Step 1: Build Container Images

In project root dir:

* docker-compose build

docker-compose will then get the container image files (if you haven't built the app before)

### Step 2: Run Container Orchestration

In project root dir:

* docker-compose up (with streaming logs)
* docker-compose up -d (with no logs)

This will automatically start the DB first, and make the other container wait until its available.

### Step 3: POST to /data/load_pickle to load XLS data

The data is loaded from a pickle (to prevent needless processing on every boot)
when a POST request is sent to this endpoint.

(you must have a valid token to POST to this endpoint, you can use the PgAdmin or the API itself to verify data is loaded)

## Important URIs

* PgAdmin
  * http://localhost:8050
  * Email/PW in .env file
* Postgres
  * http://localhost:5432
  * User is postgres, PW is in .env
* Our API
  * http://localhost:8000
  * Will redirect to documentation

## Security

This API is secured via JWT tokens set in header, after creating a user, we can POST
to /login and will get back an access and refresh token as strings. 

This API recognizes a token in the form of:
* Authorization: Bearer $(your_token)

(The only endpoint that isn't protected is /auth/login, but other than that, nothing comes in or out without a valid token)

Access tokens expire every 30 mins and need to be refreshed, refresh tokens expire in an hour and 
are used with the /auth/refresh endpoint by setting the refresh token in your auth header and POST-ing to it. 

It will return a new set of tokens as JSON.

Logout is implemented via the revocation of a user's access token, after revocation it will be added to a list in-memory. 
Almost every request to this API needs an access token and so, this mitigates the issue of stolen access tokens.

The same is true for refresh token, while they do expire after an hour, we have the ability to manually revoke
refresh tokens. 

This means that even if someone steals your access token AND your refresh token, they will not have the abilty to keep generating tokens (impersonate) as you.

(Typically you'd have password input validation (make sure PW is strong) and store the token revocation list in something like Redis, but I didn't want to add further complexity to this project)
## Documentation
Because this project is based on FastAPI and supports the OpenAPI spec,
it is self documenting.

Just navigate a browser to:
* http://localhost:8000/

You will see docs for every single endpoint as well as their request and response schemas. 

It is an easy way of interacting with the API via a simple GUI.

(Remember though, you will still have to login and set your authorization header to interact with the API. 
ModHeader is a good Chrome plugin for this.)


## Config

This app is configured via the .env file in the root, which is then read by our Pydantic
settings class and then relayed to the rest of the app.

It is also used to set env vars for our container, providing a centralized config point.

(The default Email/PW for our PgAdmin container and our Postgres container are contained within, use them
when trying to login into a container.

## License

This project is licensed under the terms of the MIT license.

## Personal Note

Hey Ivan,

I'm sorry this took so long...I (somewhat foolishly) decided that I wanted to really challenge myself.

The only tools I knew involved in this project were postgres/docker/pandas 

Everything else in the stack, I learned over the course three days while my mom was in town from Florida and mostly implemented today after work... 

I hope you like it!

- Luis