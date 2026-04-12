from src.models import User


class UserRepository:
    @staticmethod
    def create_user(password: str, **kwargs):
        return User.objects.create_user(password=password, **kwargs)

    @staticmethod
    def get_by_id(user_id: int):
        return User.objects.select_related("clinic").filter(id=user_id).first()

    @staticmethod
    def get_by_username(username: str):
        return User.objects.filter(username=username).first()

    @staticmethod
    def get_by_email(email: str):
        return User.objects.filter(email=email).first()

    @staticmethod
    def save(user: User):
        user.save()
        return user
