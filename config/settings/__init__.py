import os
if  os.environ.get("DEBUG") == "False":
    from .prod import *
else:
    from .dev import *
