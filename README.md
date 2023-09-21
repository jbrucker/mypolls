# KU Polls App

This repository contains the complete code for the KU Polls application, including the Iteration 3 changes in the domain model.

----

## Setup

*The application requires Python 3.8.*

1. (Recommended) Create a virtual environment and install dependencies as in requirements.txt.
   ```bash
   # you know how to do this
   ```
   Then activate the virtual env.

2. Run migrations (replace `python` with whatever your Python 3 command is):
   ```bash
   python manage.py migrate
   ```

3. Import data  from the `data/` directory.  For lame Windows shells, replace data/ with `data\`.
   ```bash
   python manage.py loaddata data/*.json
   ```
   This creates 4 polls, 10 users, and 1 superuser named `admin` with password `superman`

4. Set environment variables.  The default values in [mysite/settings.py](./mysite/settings.py) should work, but you may specify any of these values in `.env`:
   ```
   # Default value of DEBUG is False. True may help you with debugging.
   DEBUG = True
   ALLOWED_HOSTS = localhost,testserver,127.0.0.1,::1
   SECRET_KEY =  (a random string)
   ```

## Running the application

```bash
  python manage.py runserver
```
and navigate to [http://localhost:8000/polls/](http://localhost:8000/polls/).


## Sample Users and Votes

The data you imported from `data/users.json` (in Setup) defines these users:

| Username              | Password      |
|:----------------------|:--------------|
| demo1 ... demo9       | hackme        |
| hacker                | hackme        |

to help you test your code:

- `demo1` - `demo6` voted for all 4 poll questions.
- `demo7` - `demo9` have not voted for any poll questions.
- `hacker` has voted for some poll questions.
