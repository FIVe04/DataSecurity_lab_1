from app.crud.user import get_user_by_username, add_user
from app.database import init_db, get_db
from app.models.user import User
from app.services.crypto import get_password_hash, verify_password

init_db()

user = User(username="test", hashed_password=get_password_hash('123'), role="admin", is_locked=False, password_restrictions_enabled=False)

# with get_db() as db:
#     add_user(db=db, user=user)

with get_db() as db:
    user = get_user_by_username(db, "test")
    hp = user.hashed_password
    print(verify_password('123', hp))





