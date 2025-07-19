# Super Momos

A Python application for modeling expenses, built with FastAPI, Polars, Alembic, and dependency-injector.

## Requirements

- Python 3.13
- [uv](https://github.com/astral-sh/uv) - Modern Python package installer and resolver

## Getting Started with uv

This project uses uv for dependency management. Here are the basic commands to get started:

### Installation

First, install uv if you haven't already:

```bash
# Install uv using pip
pip install uv

# Or using curl (macOS/Linux)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or using PowerShell (Windows)
irm https://astral.sh/uv/install.ps1 | iex
```

### Setting Up the Environment

Create a virtual environment and install dependencies:

```bash
# Create a virtual environment
uv venv

# Activate the virtual environment
# On macOS/Linux:
source .venv/bin/activate
# On Windows:
.venv\Scripts\activate

# Install dependencies
uv pip install -e .

# Install development dependencies
uv pip install -e ".[dev]"
```

### Managing Dependencies

Add new dependencies:

```bash
# Add a new dependency
uv pip install package_name

# Add a new development dependency
uv pip install --dev package_name

# Update dependencies
uv pip sync
```

### Updating pyproject.toml

After installing new packages, update your pyproject.toml:

```bash
# List installed packages to help you update pyproject.toml
uv pip list

# Export requirements to a file (if needed)
uv pip freeze > requirements.txt
```

### Testing 
```sh
alembic upgrade head # which is to update database schema & run seeding data
```

### Explanation 
#### Question 1:
- I believe that our data schema model is good enough in order to serve our use case from the assignment
#### Question 2:
- I implemented the very simple router to handle user retrieval. The version you are viewing is the improved version. More explanation in Q3 Section.


- My assumption here is the idea to send email for user when they got the event such as (Transaction Completed, Event Created, Canceled). Since the notification is a huge topic and require a trivia effort (an simple endpoint which got input and write log to indicate email was sent not really worth it to implement) and that approach (using the endpoint) to send email for a user in any case, really a bad design and couldnt fit with large data thruput.

- And I did already have an little design about notification system. which is rely on kafka and scalable. So for that part "email sending", please check the design at here: https://lucid.app/lucidchart/982ef936-7c39-46d2-a088-933eecdf9624/view

#### Question 3
- The main problem of the design using `User`, `Event`, and `Registration` tables is CPU-extensive effort will be put in the database instance when we query number of event hosted/attended. If we merge filter query(job, company, state, ...) & agg query (number of events) into 1 query that will be a huge problem in terms of maintenance effort. More or less, we have to sacrifice between memory/time complexity. In order to solve that we can take many approach such as using Redis as cache layer, back populate event count on update, trigger on update, migrate to Elastic Search. From my end. I will take the back populate script on update. Which mean that when user register an event, not only we have create new registration but also increase the number of event count on the user side.

- Since we have a large dataset, key-set pagination is preferred. 
- Another problem is the sending email endpoint, which I believed that writing an endpoint for that purpose is not a good idea. The logic to decide when, which, what to send notification to user (email) should be handle separately. I also mention about the architect design above.

#### Question 4
For query user
```sh
curl --location 'http://localhost:8000/api/users?min_events_attended=10&max_events_attended=20' 
curl --location 'http://localhost:8000/api/users?min_events_attended=10'
curl --location 'http://localhost:8000/api/users?max_events_attended=20'
curl --location 'http://localhost:8000/api/users?min_events_hosted=1&max_events_hosted=3'
curl --location 'http://localhost:8000/api/users?last_name=Howad&min_events_attended=10' | jq

```