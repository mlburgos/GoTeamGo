Requirements
    
    Flask==0.11
    Flask-DebugToolbar==0.10.0
    Flask-SQLAlchemy==2.0
    Jinja2==2.7.3
    MarkupSafe==0.23
    SQLAlchemy==1.0.3
    Werkzeug==0.10.4
    blinker==1.3
    itsdangerous==0.24
    wsgiref==0.1.2
    psycopg2


Setup

    Launch and activate a virtual environment

        $ virtualenv env
        $ source env/bin/activate

    Install Python 2.7

    pip install requirements
        
        $ pip install -r requirements.txt


    Create and seed the database

        $ createdb go_team_go
        $ python model.py
        $ python sample_data.py

    Launch server

        $ python server.py

    View app at:
    
        http://localhost:5000/


Test it out!

    Register as a new user to:
        - log a workout 
        - request to join a group (try Group1)
        - create a new group
        - add a photo
        - set a personal goal 

    Login as User3 to play around with features:

        email: User3@gmail.com 
        password: pswd1

        Features to try:
        - log a new workout
        - view your groups
        - view your friends
        - as an admin, approve pending requests to join groups
        - add/change your photo
        - create a new group
        - request to join another group

