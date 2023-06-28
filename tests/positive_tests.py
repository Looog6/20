import random
from api import PetFriends
from config import valid_email, valid_password, images
import os


pf = PetFriends()

''' 1. Сценарий (позитивный сценарий бизнес логики)'''


#       1.1. Получить ключ API
def test_get_key_1(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result, res = pf.get_api_key(email, password)
    print(f'\n', result)
    auth_key = result['key']
    print(result['key'])
    print(type(auth_key), auth_key)
    print('\nres', res)
    print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?
    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result  # - есть key отлично иначе error
    assert res.headers['Content-Type'] == 'application/json'  # - проверка response headers
    assert 'Date' in res.headers  # - проверка response headers
    return result


# 		1.2. Добавить информацию о новом питомце №1 без фото
def test_successful_add_self_pet_without_photo(name='Бобр - без фото', animal_type='Собака', age=2):
    """Проверяем возможность добавления питомца без фото"""

    # Получаем ключ auth_key
    _, auth_key, res = pf.get_api_key(valid_email, valid_password)

    # Добавляем питомца его имя, вид и возраст
    status, result, res = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)

    print('\nheaders', res.headers)
    print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?

    # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
    assert status == 200
    assert result['name'] == name
    assert res.headers['Content-Type'] == 'application/json'  # - проверка response headers
    assert 'Date' in res.headers  # - проверка response headers


# 		1.3. Добавить информацию о новом питомце №2 с фото
def test_add_new_pet_with_valid_data(name='Бобр', animal_type='Собака', age='5',
                                       pet_photo=f'images/{random.choice(images)}'):
    """Проверяем что можно добавить питомца с валидными данными"""

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key, _ = pf.get_api_key(valid_email, valid_password)
    print("\nauth_key", auth_key)

    # Добавляем питомца
    status, result, res = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    print("#1.3 status", status)
    print("#1.4 result", result)

    print('\nheaders', res.headers)
    print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name
    # assert res.headers['content-type'] == 'text/html; charset=utf-8'  # - Ожидаемый ответ в swagger
    assert res.headers['content-type'] == 'application/json'  # - Фактический результат
    '''В swagger  content-type: text/html; charset=utf-8, а по факту приходит 'application/json
    ЭТО БАГ?'''
    assert 'Date' in res.headers  # - проверка response headers


# 		1.4. Добавить фото питомцу
def test_successful_changes_pet_photo_1(pet_photo=f'images/{random.choice(images)}'):
    """Тестируем: Изменение фото питомца"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    print('pet_photo', pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    _, auth_key, _ = pf.get_api_key(valid_email, valid_password)
    print("\nauth_key", auth_key)
    _, my_pets, _ = pf.get_list_of_pets(auth_key, "my_pets")
    print("\nmy_pets", my_pets)

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Рекс", "Кот", "2", "images/107.jpg")
        _, my_pets, _ = pf.get_list_of_pets(auth_key, "my_pets")

    pet_id = my_pets['pets'][0]['id']  # id питомца (первый в списке)
    image = my_pets['pets'][0]['pet_photo']  # получаем код image изменяемой картинки питомца

    # Добавляем питомца с фото
    status, result, res = pf.add_pet_photo(auth_key, pet_id, pet_photo)

    print('\nheaders', res.headers)
    print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    # Если значению кода изменяемой картинки не равно полученному значению кода картинки в ответе - PASSED:
    assert image != result.get('pet_photo')  # - есть ответ от сервера и можно сравнить результаты
    # assert res.headers['content-type'] == 'text/html; charset=utf-8'  # - Ожидаемый ответ в swagger
    assert res.headers['content-type'] == 'application/json'  # - Фактический результат
    '''В swagger  content-type: text/html; charset=utf-8, а по факту приходит 'application/json
    ЭТО БАГ?'''
    assert 'Date' in res.headers  # - проверка response headers


# 		1.5. Изменить информацию о питомце
def test_successful_update_self_pet_info_1(name='Лорд', animal_type='', age=''):
    """Проверяем возможность обновления информации о питомце и выполняем проверку, что не изменились другие данные"""

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key, _ = pf.get_api_key(valid_email, valid_password)
    _, my_pets, res = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result, res = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
        assert result['animal_type'] != animal_type
        assert result['age'] != age
        print('\nheaders', res.headers)
        print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?
        # assert res.headers['content-type'] == 'text/html; charset=utf-8'  # - Ожидаемый ответ в swagger
        assert res.headers['content-type'] == 'application/json'  # - Фактический результат
        '''В swagger  content-type: text/html; charset=utf-8, а по факту приходит 'application/json
        ЭТО БАГ?'''
        assert 'Date' in res.headers  # - проверка response headers

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")


# 		1.6. Получить список питомцев
def test_get_my_pets_with_valid_key_1(filter='my_pets'):  # - тест падает если список пустой
    """ Проверяем что запрос с фильтром мои питомцы возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этот ключ
    запрашиваем список питомцев применив filter - 'my_pets' и проверяем что список не пустой."""

    _, auth_key, _ = pf.get_api_key(valid_email, valid_password)
    status, result, res = pf.get_list_of_pets(auth_key, filter)

    if len(result['pets']) > 0:

        assert status == 200
        print('len', len(result['pets']), result)
        assert len(['pets']) > 0

    else:
        # если список питомцев пустой, то выкидываем исключение с текстом об отсутствии своих питомцев
        raise Exception("There is no my pets")
    """Нужно довести до ума работу исключений, чтобы тест проходил успешно"""


# 		1.7. Удалить питомца
def test_successful_delete_self_pet_1():
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    _, auth_key, _ = pf.get_api_key(valid_email, valid_password)
    _, my_pets, _ = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, result, res = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets, _ = pf.get_list_of_pets(auth_key, "my_pets")

    print('\nheaders', res.headers)
    print('\ncookies', res.cookies)  # - мое мнение куки нет, но как их правильно проверить?

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    # assert pet_id not in my_pets.values()
    assert res.headers['content-type'] == 'text/html; charset=utf-8'
    assert 'Date' in res.headers  # - проверка response headers (как проверить актуальность даты?)
