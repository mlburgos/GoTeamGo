Requirements
    
    appdirs==1.4.0
    bcrypt==3.1.2
    blinker==1.3
    cffi==1.9.1
    click==6.7
    decorator==4.0.11
    enum34==1.1.6
    Flask==0.11
    Flask-Bcrypt==0.7.1
    Flask-DebugToolbar==0.10.0
    Flask-SQLAlchemy==2.0
    functools32==3.2.3.post2
    ipython-genutils==0.1.0
    itsdangerous==0.24
    Jinja2==2.7.3
    jsonschema==2.6.0
    jupyter-core==4.3.0
    MarkupSafe==0.23
    nbformat==4.3.0
    packaging==16.8
    pkg-resources==0.0.0
    plotly==2.0.2
    psycopg2==2.6.2
    pycparser==2.17
    pyparsing==2.1.10
    pytz==2016.10
    requests==2.13.0
    six==1.10.0
    SQLAlchemy==1.0.3
    traitlets==4.3.1
    Werkzeug==0.10.4

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

