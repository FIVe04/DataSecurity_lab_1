from app.core.config import settings
from app.crud.user import get_user_by_username, add_user, update_user_password, get_user_by_id, register_user
from app.database import get_db
from app.models.user import User
from app.services.crypto import verify_password, get_password_hash
from app.services.password_restrictions import check_password


class UserState:
    def __init__(self):
        self.id = None
        self.is_logged_in = False
        self.is_admin = False
        self.username = None
        self.login_attempts = 0

    def logout(self):
        print('logout')
        self.id = None
        self.is_logged_in = False
        self.is_admin = False
        self.username = None
        self.login_attempts = 0

    def change_password(self, old_password, new_password):
        new_password_hash = get_password_hash(self.username, new_password)
        try:
            with get_db() as db:
                old_user = get_user_by_id(db, self.id)
                print(old_user, self.id)
                if verify_password(old_user.username, old_password, old_user.hashed_password):
                    if old_user.password_restrictions_enabled:
                        error_password = check_password(new_password)
                        if error_password:
                            return {'message': error_password, 'detail': None}
                    new_user = update_user_password(db, self.id, new_password_hash)
                    return {'message': 'OK', 'detail': 'password updated successfully'}
                return {'message': 'Wrong password', 'detail': 'Wrong password'}
        except Exception as e:
            return {'message': str(e), 'detail': e}

    def login(self, username, password):
        self.is_logged_in = False
        try:
            with get_db() as db:
                user = get_user_by_username(db, username)

                if user:
                    if user.hashed_password == "":
                        return {'message': "You should register first!", 'data': {'user_id': user.id}}
                    if verify_password(user.username, password, user.hashed_password):
                        if user.is_locked:
                            return {'message': 'User is locked', 'data': None}
                        self.is_logged_in = True
                        self.is_admin = user.role == 'admin'
                        self.username = user.username
                        self.id = user.id
                        self.login_attempts = 0
                        return {'message': 'OK', 'data': {'user_id': user.id}}
                    self.login_attempts += 1
                    if self.login_attempts >= settings.LOGIN_ATTEMPTS:
                        return {'message': 'You have exceeded maximum login attempts', 'data': None}
                    return {'message': 'Wrong username or password', 'data': None}
                else:
                    self.login_attempts += 1
                    if self.login_attempts >= settings.LOGIN_ATTEMPTS:
                        return {'message': 'You have exceeded maximum login attempts', 'data': None}
                    return {'message': 'Wrong username or password', 'data': None}
        except Exception as e:
            return {'message': str(e), 'data': {'error': e}}

    def register(self, username, password):
        self.is_logged_in = False
        try:
            with get_db() as db:
                user = get_user_by_username(db, username)
                if user:
                    if user.hashed_password == "":
                        if user.is_locked:
                            return {'message': 'User is locked', 'data': None}
                        if user.password_restrictions_enabled:
                            response_password_check = check_password(password)
                            if response_password_check:
                                return {'message': response_password_check, 'data': None}

                        new_user = User(username=username, hashed_password=get_password_hash(user.username, password),
                                        role=user.role, is_locked=False, password_restrictions_enabled=False)
                        ref_user = register_user(db, new_user)
                        self.is_admin = ref_user.role == 'admin'
                        self.is_logged_in = True
                        self.id = ref_user.id
                        self.username = ref_user.username
                        print('logged_in', self.id)
                        return {'message': 'OK', 'data': {'user_id': ref_user.id}}
                    return {'message': 'User already exists', 'data': None}
                return {'message': 'No such user', 'data': None}
        except Exception as e:
            return {'message': str(e), 'data': {'error': e}}


    def add_user_from_admin(self, username, is_locked, password_restrictions_enabled):
        try:
            with get_db() as db:
                new_user = User(username=username, hashed_password="",
                                role='user', is_locked=is_locked,
                                password_restrictions_enabled=password_restrictions_enabled)
                add_user(db, new_user)
                return {'message': 'OK', 'data': {'user_id': new_user.id}}
        except Exception as e:
            return {'message': str(e), 'data': {'error': e}}

