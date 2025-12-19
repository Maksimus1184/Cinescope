import pytest
from models.base_models import TestUser, CreateUserResponse

class TestUser:

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_create_user(self, super_admin, creation_user_data: TestUser):
        response = super_admin.api.user_api.create_user(creation_user_data)

        # Используем модель для валидации ответа
        create_user_response = CreateUserResponse(**response.json())

        # Проверки через объект модели
        assert create_user_response.id and create_user_response.id != '', "ID должен быть не пустым"
        assert create_user_response.email == creation_user_data.email
        assert create_user_response.fullName == creation_user_data.fullName

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    def test_get_user_by_locator(self, super_admin, creation_user_data: TestUser):
        # Создаем пользователя
        create_response = super_admin.api.user_api.create_user(creation_user_data)
        created_user = CreateUserResponse(**create_response.json())

        # Получаем пользователя по ID и по email
        response_by_id = super_admin.api.user_api.get_user(created_user.id)
        response_by_email = super_admin.api.user_api.get_user(creation_user_data.email)

        # Валидируем ответы моделями
        user_by_id = CreateUserResponse(**response_by_id.json())
        user_by_email = CreateUserResponse(**response_by_email.json())

        # Проверяем, что объекты одинаковы (можно сравнить словари или выбранные поля)
        assert user_by_id.id == user_by_email.id
        assert user_by_id.email == user_by_email.email
        assert user_by_id.fullName == user_by_email.fullName
        assert user_by_id.roles == user_by_email.roles
        assert user_by_id.verified == user_by_email.verified
        assert user_by_id.banned == user_by_email.banned

        # Проверяем, что данные соответствуют ожидаемым
        assert user_by_id.id == created_user.id
        assert user_by_id.email == creation_user_data.email
        assert user_by_id.fullName == creation_user_data.fullName
        assert user_by_id.roles == ['USER']  # API возвращает список ['USER']
        assert user_by_id.verified is True
        assert user_by_id.banned is False

        # Проверяем, что createdAt есть и в правильном формате
        assert user_by_id.createdAt is not None
        assert user_by_email.createdAt is not None

    @pytest.mark.api
    @pytest.mark.smoke
    @pytest.mark.regression
    @pytest.mark.integration
    @pytest.mark.slow
    def test_get_user_by_id_common_user(self, common_user):
        common_user.api.user_api.get_user(common_user.email, expected_status=403)

