# comeup with user model that supports roles (done)
# simple user registration (done)
# sign in (done)
# sign out (done)
# roles (done)
# user has different roles (done)
# restricting with roles (done)

from flask import (
        Flask,
        Response,
        redirect,
        render_template,
        url_for,
        request,
        session,
        current_app,
        g
        )

from flask.ext.principal import (
        Principal,
        UserNeed,
        RoleNeed,
        Permission,
        Identity,
        identity_changed,
        identity_loaded,
        AnonymousIdentity
        )
from flask.ext.login import (
        login_required,
        login_user,
        logout_user,
        current_user,
        LoginManager,
        AnonymousUserMixin
        )
from database import db_session
from models import User
from forms import RegistrationForm, LoginForm


app = Flask(__name__)

# config
app.config.update(
    DEBUG=True,
    SECRET_KEY='secret_xxx'
)


class CustomAnonymousUser(AnonymousUserMixin):

    def is_anonymous(self):
        return True

    def is_authenticated(self):
        return False

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.anonymous_user = CustomAnonymousUser



# flask-principal
principals = Principal(app)
normal_role = RoleNeed('normal_user')
normal_permission = Permission(normal_role)

admin_role = RoleNeed('admin')
admin_permission = Permission(admin_role)

project_manager_role = RoleNeed('project_manager')
project_manager_permission = Permission(project_manager_role)

# Setting permissions for project creation
project_creation_permission = Permission(
        admin_role,
        project_manager_role
        )




@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect("/")

    form = RegistrationForm(request.form)
    if request.method == 'POST':
        user = User(
                email=form.email.data,
                password=form.password.data
                )
        db_session.add(user)
        db_session.commit()
        return redirect('/login')
    else:
        return render_template("register.html", form=form)


@login_manager.user_loader
def user_loader(user_id):
    return User.query.get(user_id)


@identity_loaded.connect_via(app)
def on_identity_loaded(sender, identity):
    identity.user = current_user

    if hasattr(current_user, 'id'):
        identity.provides.add(UserNeed(current_user.id))

    if hasattr(current_user, 'role'):
        role = current_user.role
        identity.provides.add(RoleNeed(role))


@app.before_request
def set_identity():
    if current_user and not current_user.is_anonymous():
        if not hasattr(g, 'identity'):
            g.identity = Identity(current_user.id)
    else:
        if not hasattr(g, 'identity'):
            g.identity = AnonymousIdentity()

# we'd like to protect this resource
@app.route('/')
@normal_permission.require(http_exception=403)
def home():
    return Response("Hello World!")


@app.route('/create_project')
@project_creation_permission.require(http_exception=403)
def create_project():
    return Response("You can create projects here")


@app.route('/admin')
@admin_permission.require(http_exception=403)
def admin():
    return Response("Hello Admin!")


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated() and g.identity.can(normal_permission):
        return redirect('/')
    else:
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(email=form.email.data).first()
            if user and user.password == form.password.data:
                user.authenticated = True
                db_session.add(user)
                db_session.commit()
                login_user(user)
                g.identity = Identity(user.id)
                identity_changed.send(app, identity=g.identity)
                return redirect(url_for("home"))
    return render_template("login.html", form=form)


@app.route("/logout", methods=["GET"])
@login_required
def logout():
    user = current_user
    user.authenticated = False
    db_session.add(user)
    db_session.commit()
    logout_user()
    for key in ('identity.email', 'identity.auth_type'):
        session.pop(key, None)
    identity_changed.send(current_app._get_current_object(),
                          identity=AnonymousIdentity())
    g.identity = AnonymousIdentity()
    return redirect(url_for("login"))


# somewhere to logout
@app.route("/logout")
def signout():
    # this does not work yet():
    pass


# handle login failed
@app.errorhandler(401)
def page_not_found(e):
    return Response('Login failed')


@app.errorhandler(403)
def page_not_found(e):
    print "### permission denied #######"
    session['redirected_from'] = request.url
    return redirect(url_for('login'))


if __name__ == "__main__":
    app.run()
