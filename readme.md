![Tests](https://github.com/uwidcit/flaskmvc/actions/workflows/dev.yml/badge.svg)

# Flask MVC Template
A template for flask applications structured in the Model View Controller pattern [Demo](https://dcit-flaskmvc.herokuapp.com/). [Postman Collection](https://documenter.getpostman.com/view/583570/2s83zcTnEJ)


# Dependencies
* Python3/pip3
* Packages listed in requirements.txt

# Installing Dependencies
```bash
$ pip install -r requirements.txt
```

# Configuration Management


Configuration information such as the database url/port, credentials, API keys etc are to be supplied to the application. However, it is bad practice to stage production information in publicly visible repositories.
Instead, all config is provided by a config file or via [environment variables](https://linuxize.com/post/how-to-set-and-list-environment-variables-in-linux/).

## In Development

When running the project in a development environment (such as gitpod) the app is configured via default_config.py file in the App folder. By default, the config for development uses a sqlite database.

default_config.py
```python
SQLALCHEMY_DATABASE_URI = "sqlite:///temp-database.db"
SECRET_KEY = "secret key"
JWT_ACCESS_TOKEN_EXPIRES = 7
ENV = "DEVELOPMENT"
```

These values would be imported and added to the app in load_config() function in config.py

config.py
```python
# must be updated to inlude addtional secrets/ api keys & use a gitignored custom-config file instad
def load_config():
    config = {'ENV': os.environ.get('ENV', 'DEVELOPMENT')}
    delta = 7
    if config['ENV'] == "DEVELOPMENT":
        from .default_config import JWT_ACCESS_TOKEN_EXPIRES, SQLALCHEMY_DATABASE_URI, SECRET_KEY
        config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
        config['SECRET_KEY'] = SECRET_KEY
        delta = JWT_ACCESS_TOKEN_EXPIRES
...
```

## In Production

When deploying your application to production/staging you must pass
in configuration information via environment tab of your render project's dashboard.

![perms](./images/fig1.png)

# Flask Commands

wsgi.py is a utility script for performing various tasks related to the project. You can use it to import and test any code in the project. 
You just need create a manager command function, for example:

```python
# inside wsgi.py

user_cli = AppGroup('user', help='User object commands')

@user_cli.cli.command("create-user")
@click.argument("username")
@click.argument("password")
def create_user_command(username, password):
    create_user(username, password)
    print(f'{username} created!')

app.cli.add_command(user_cli) # add the group to the cli

```

Then execute the command invoking with flask cli with command name and the relevant parameters

```bash
$ flask user create bob bobpass
```


# Running the Project

_For development run the serve command (what you execute):_
```bash
$ flask run
```

# Run in Postman

[<img src="https://run.pstmn.io/button.svg" alt="Run In Postman" style="width: 128px; height: 32px;">](https://app.getpostman.com/run-collection/42343436-c0eac877-b2db-4d9d-84c9-1de123338aba?action=collection%2Ffork&source=rip_markdown&collection-url=entityId%3D42343436-c0eac877-b2db-4d9d-84c9-1de123338aba%26entityType%3Dcollection%26workspaceId%3D5fde46e6-c901-4ef7-ac25-706d39627662#?env%5BRosterApp%20Local%5D=W3sia2V5IjoiYmFzZV91cmwiLCJ2YWx1ZSI6IiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiaHR0cDovL2xvY2FsaG9zdDo4MDgwIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiJodHRwOi8vbG9jYWxob3N0OjgwODAiLCJzZXNzaW9uSW5kZXgiOjB9LHsia2V5IjoiYWRtaW5fdXNlcm5hbWUiLCJ2YWx1ZSI6IiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiYm9iIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiJib2IiLCJzZXNzaW9uSW5kZXgiOjF9LHsia2V5IjoiYWRtaW5fcGFzc3dvcmQiLCJ2YWx1ZSI6IiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiYm9icGFzcyIsImNvbXBsZXRlU2Vzc2lvblZhbHVlIjoiYm9icGFzcyIsInNlc3Npb25JbmRleCI6Mn0seyJrZXkiOiJzdGFmZl91c2VybmFtZSIsInZhbHVlIjoiIiwiZW5hYmxlZCI6dHJ1ZSwidHlwZSI6ImRlZmF1bHQiLCJzZXNzaW9uVmFsdWUiOiJqYW5lIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiJqYW5lIiwic2Vzc2lvbkluZGV4IjozfSx7ImtleSI6InN0YWZmX3Bhc3N3b3JkIiwidmFsdWUiOiIiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiZGVmYXVsdCIsInNlc3Npb25WYWx1ZSI6ImphbmVwYXNzIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiJqYW5lcGFzcyIsInNlc3Npb25JbmRleCI6NH0seyJrZXkiOiJzY2hlZHVsZV9pZCIsInZhbHVlIjoiIiwiZW5hYmxlZCI6dHJ1ZSwidHlwZSI6ImRlZmF1bHQiLCJzZXNzaW9uVmFsdWUiOiIxIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOjEsInNlc3Npb25JbmRleCI6NX0seyJrZXkiOiJzaGlmdF9pZCIsInZhbHVlIjoiIiwiZW5hYmxlZCI6dHJ1ZSwidHlwZSI6ImRlZmF1bHQiLCJzZXNzaW9uVmFsdWUiOiIxIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOjEsInNlc3Npb25JbmRleCI6Nn0seyJrZXkiOiJub3RpZmljYXRpb25faWQiLCJ2YWx1ZSI6IiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJkZWZhdWx0Iiwic2Vzc2lvblZhbHVlIjoiIiwiY29tcGxldGVTZXNzaW9uVmFsdWUiOiIiLCJzZXNzaW9uSW5kZXgiOjd9LHsia2V5IjoiYWRtaW5fdG9rZW4iLCJ2YWx1ZSI6IiIsImVuYWJsZWQiOnRydWUsInR5cGUiOiJhbnkiLCJzZXNzaW9uVmFsdWUiOiJleUpoYkdjaU9pSklVekkxTmlJc0luUjVjQ0k2SWtwWFZDSjkuZXlKbWNtVnphQ0k2Wm1Gc2MyVXNJbWxoZENJNk1UYzJORGMzTnprNE9Td2lhblJwSWpvaVpUTTROalZoWm1VdE5qWmtPQzAwWlRZNExUaGtPRFF0TVRjM1pqQTRPVFkyTnpobS4uLiIsImNvbXBsZXRlU2Vzc2lvblZhbHVlIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1jbVZ6YUNJNlptRnNjMlVzSW1saGRDSTZNVGMyTkRjM056azRPU3dpYW5ScElqb2laVE00TmpWaFptVXROalprT0MwMFpUWTRMVGhrT0RRdE1UYzNaakE0T1RZMk56aG1JaXdpZEhsd1pTSTZJbUZqWTJWemN5SXNJbk4xWWlJNklqRWlMQ0p1WW1ZaU9qRTNOalEzTnpjNU9Ea3NJbVY0Y0NJNk1UYzJORGMzT0RnNE9YMC40UFhONHY4bTk2bFJXTm5DU2M3clpmWGtqd0NjZXl4Y0RLZGhwSXMtMXU4Iiwic2Vzc2lvbkluZGV4Ijo4fSx7ImtleSI6InN0YWZmX3Rva2VuIiwidmFsdWUiOiIiLCJlbmFibGVkIjp0cnVlLCJ0eXBlIjoiYW55Iiwic2Vzc2lvblZhbHVlIjoiZXlKaGJHY2lPaUpJVXpJMU5pSXNJblI1Y0NJNklrcFhWQ0o5LmV5Sm1jbVZ6YUNJNlptRnNjMlVzSW1saGRDSTZNVGMyTkRjM09EQXpNU3dpYW5ScElqb2laR1JoWmpNME5EZ3RZekJoWVMwME9HSTFMVGt5TldFdE5EazJOR0ppTkRWaE5HVTIuLi4iLCJjb21wbGV0ZVNlc3Npb25WYWx1ZSI6ImV5SmhiR2NpT2lKSVV6STFOaUlzSW5SNWNDSTZJa3BYVkNKOS5leUptY21WemFDSTZabUZzYzJVc0ltbGhkQ0k2TVRjMk5EYzNPREF6TVN3aWFuUnBJam9pWkdSaFpqTTBORGd0WXpCaFlTMDBPR0kxTFRreU5XRXRORGsyTkdKaU5EVmhOR1UySWl3aWRIbHdaU0k2SW1GalkyVnpjeUlzSW5OMVlpSTZJaklpTENKdVltWWlPakUzTmpRM056Z3dNekVzSW1WNGNDSTZNVGMyTkRjM09Ea3pNWDAuRXJ0X0huajRvTGxoS1pXb2JjWGJPbHlHb015enE2QUpHbGZiRUljaVdUOCIsInNlc3Npb25JbmRleCI6OX1d)


_For production using gunicorn (what the production server executes):_
```bash
$ gunicorn wsgi:app
```

# Deploying
You can deploy your version of this app to render by clicking on the "Deploy to Render" link above.

# Initializing the Database
When connecting the project to a fresh empty database ensure the appropriate configuration is set then file then run the following command. This must also be executed once when running the app on heroku by opening the heroku console, executing bash and running the command in the dyno.

This creates 4 users id 1 is the admin, id 2 and 3 are staff and 4 is a user
```bash
$ flask init
```
# User Management

Create Users

After flask type user create then add the username, the password and the role of the user (either admin, staff or user)

```bash
flask user create admin1 adminpass admin
```
List users
```bash
flask user list string
flask user list json
```
# Managing shifts

To Schedule shifts (Admin only)

After flask type shift  schedule the staff id, the schedule idand the start and end of the shift in the ISO 8601 DateTime with time format( can copy the formant below and edit it)

```bash
flask shift schedule 2 1 2025-10-01T09:00:00 2025-10-01T17:00:00
```
View Roster (Staff only)

After flask type shift roster to for the logged in staff

```bash
flask shift roster 
```
Clockin and Clockout(Staff only)

After flask type shift clockin or clockoutand the shift id

```bash
flask shift clockin 1
flask shift clockout 1
```

Shift Report (Admin only)

After flask  type shift report 

```bash
flask shift report 
```

# Managing schedule

Create Schedule(Admin only)

After flask type schedule, create and the title 

```bash
flask schedule create "April Week 2" 
```

List All Schedules(Admin only)

After flask  type schedule  list 

```bash
flask schedule list 
```
View a Schedule (Admin only)

After flask type schedule view and the schedule id 

```bash
flask schedule view 1 
```

# Database Migrations
If changes to the models are made, the database must be'migrated' so that it can be synced with the new models.
Then execute following commands using manage.py. More info [here](https://flask-migrate.readthedocs.io/en/latest/)

```bash
$ flask db init
$ flask db migrate
$ flask db upgrade
$ flask db --help
```

# Testing

## Unit & Integration
Unit and Integration tests are created in the App/test. You can then create commands to run them. Look at the unit test command in wsgi.py for example

```python
@test.command("user", help="Run User tests")
@click.argument("type", default="all")
def user_tests_command(type):
    if type == "unit":
        sys.exit(pytest.main(["-k", "UserUnitTests"]))
    elif type == "int":
        sys.exit(pytest.main(["-k", "UserIntegrationTests"]))
    else:
        sys.exit(pytest.main(["-k", "User"]))
```

You can then execute all user tests as follows

```bash
$ flask test user
```

You can also supply "unit" or "int" at the end of the comand to execute only unit or integration tests.

You can run all application tests with the following command

```bash
$ pytest
```

## Test Coverage

You can generate a report on your test coverage via the following command

```bash
$ coverage report
```

You can also generate a detailed html report in a directory named htmlcov with the following comand

```bash
$ coverage html
```

# Troubleshooting

## Views 404ing

If your newly created views are returning 404 ensure that they are added to the list in main.py.

```python
from App.views import (
    user_views,
    index_views
)

# New views must be imported and added to this list
views = [
    user_views,
    index_views
]
```

## Cannot Update Workflow file

If you are running into errors in gitpod when updateding your github actions file, ensure your [github permissions](https://gitpod.io/integrations) in gitpod has workflow enabled ![perms](./images/gitperms.png)

## Database Issues

If you are adding models you may need to migrate the database with the commands given in the previous database migration section. Alternateively you can delete you database file.
