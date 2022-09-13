from api.user import user

@user.get("/")
def index():
    return "hello"