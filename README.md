### Instructions to run

#### Note:
Console commands -  `$`
Python console - `>>>`

#### DB tables
```
$ ipython

>>> from database import init_db
>>> init_db()
```
#### Run the app
```
python app.py
```

#### Roles
* normal_user
* admin
* project_manager

#### Urls
```
/register
/login
/logout

/ (home for normal user)
/admin (home for admin. Only admin users can access this page )
/create_project (only project_managers, admins can access this page)
```

#### To update role for an user
```
$ ipython

>>> from database import db_session
>>> from models import User
# get user
>>> u1 = db_session.query(User).get(1)
>>> u1.role = 'admin'
>>> db_session.add(u1)
>>> db_session.commit()
```
