from flask_bootstrap import Bootstrap
from flask_wtf.csrf import CSRFProtect
# from flask_oidc import OpenIDConnect

bootstrap = Bootstrap()
csrf = CSRFProtect()
# oidc = OpenIDConnect()