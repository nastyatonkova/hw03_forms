from django.core.exceptions import ValidationError


# Функция-валидатор:
def validate_not_empty(value):
    # Проверка "а заполнено ли поле?"
    if value == '':
        raise ValidationError(
            'А кто поле будет заполнять, Пушкин?',
            params={'value': value},
        )
