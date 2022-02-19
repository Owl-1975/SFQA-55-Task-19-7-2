from api import PetFriends
from settings import valid_email, valid_password, invalid_email, invalid_password
import os

pf = PetFriends()


def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    '''Тест запроса API на возврат статуса 200 и наличие в результате слова key'''

    #Отправляем запрос и сохраняем ответ с кодом статуса в status, а текст в result
    status, result = pf.get_api_key(email, password)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert 'key' in result


def test_get_all_pets_with_valid_key(filter=''):
    '''Проверка запроса всех питомцев на возврат не пустого списка.
    Получаем API ключ, сохраняем его в auth_key. Используя ключ запрашиваем
    список всех питомцев. Проверяем что список не пустой. Доступное значение
    параметра filter - 'my_pets' или '' '''

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0


def test_add_new_pet_with_valid_data(name='KorG', animal_type='corgi', age='3', pet_photo='images/Relax.jpg'):
    '''Тест возможности добавления нового питомца с корректными данными'''

    #Получаем полный путь к файлу с изображением и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name


def test_successful_delete_self_pet():
    '''Тест удаления птомца из профиля пользователя'''

    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Проверяем список своих питомцев, если список пустой добавляем нового и повторяем запрос
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, 'СуперКорг', 'Corgi', '3', 'images/Relax.jpg')
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Отправляем запрос на удаление по ID первого в списке питомца
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    #Запрашиваем список питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Проверяем статус ответа и отсутствие ID удаленного питомца в списке
    assert status == 200
    assert pet_id not in my_pets.values()


def test_successful_update_self_pet_info(name='Корж', animal_type='Вельш Корги Пемброк', age=2):
    '''Тест изменения информации о питомце'''

    #Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    #Если список не пустой, изменяем данные
    assert len(my_pets['pets']) > 0, 'В профиле учетной записи отсутсвуют сведения о питомцах'
    status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

    #Проверяем статус ответа и соответствие имени заданному
    assert status == 200
    assert result['name'] == name


def test_add_new_pet_wo_photo_valid_data(name='КорГ без Fото', animal_type='corgi', age='1'):
    '''Тест возможности быстрого добавления нового питомца без фотографии с корректными данными'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] is ''


def test_add_photo_of_pet(pet_photo='images/Corgi_Butt.jpg'):
    '''Тест возможности добавления (изменения) фотографии в профиль питомца'''

    # Получаем полный путь к файлу с изображением и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Получаем ключ auth_key и список своих питомцев
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, изменяем данные
    assert len(my_pets['pets']) > 0, 'В профиле учетной записи отсутсвуют сведения о питомцах'
    status, result = pf.add_photo_of_pet(auth_key, my_pets['pets'][0]['id'], pet_photo)

    # Проверяем статус ответа и соответствие имени заданному
    assert status == 200
    assert result['pet_photo'] is not ''


def test_01_get_status_for_invalid_password(email=valid_email, password=invalid_password):
    '''Тест-01: Доступ к учетной записи с недействительным паролем.
    Запрос API на возврат статуса 403 при вводе недействительного пароля'''

    #Отправляем запрос и сохраняем ответ с кодом статуса в status, а текст в result
    status, result = pf.get_api_key(email, password)

    #Сверяем ожидаемый и фактический результат
    assert status == 403
    print(result)


def test_02_get_status_for_invalid_email(email=invalid_email, password=valid_password):
    '''Тест-02: Доступ к веб приложению с незарегестрированным адресом  электронной почты
    и действительным паролем существующей учетной записи. Запрос API на возврат статуса 403
    при вводе недействительных данных пользователя'''

    #Отправляем запрос и сохраняем ответ с кодом статуса в status, а текст в result
    status, result = pf.get_api_key(email, password)

    #Сверяем ожидаемый и фактический результат
    assert status == 403
    print(result)


def test_03_get_status_for_empty_reg_fields(email='', password=''):
    '''Тест-03: Доступ к веб приложению без ввода адреса электронной почты и пароля.
     Запрос API на возврат статуса 403 в связи с отсутствием в запросе данных пользователя'''

    #Отправляем запрос и сохраняем ответ с кодом статуса в status, а текст в result
    status, result = pf.get_api_key(email, password)

    #Сверяем ожидаемый и фактический результат
    assert status == 403
    print(result)


def test_04_add_new_pet_wo_photo_big_age(name='Вечный КорГ', animal_type='corgi', age='99999999999999'):
    '''Тест-04 Быстрое добавление нового питомца без фотографии с  некорректными данными вораста:
    неправдоподобное большое число.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['age'] != 0


def test_05_add_new_pet_wo_photo_negative_age(name='КорГ растущий в обратную сторону', animal_type='corgi', age='-5'):
    '''Тест-05 Быстрое добавление нового питомца без фотографии с  некорректными данными вораста:
    отрицательное число.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['age'] != 0


def test_06_add_new_pet_wo_photo_zero_age(name='КорГ без возраста', animal_type='corgi', age=''):
    '''Тест-06 Быстрое добавление нового питомца без фотографии с неуказанным возрастом.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['age'] is ''


def test_07_add_new_pet_wo_photo_alphabet_age(name='КорГ с буквами вместо возраста', animal_type='corgi', age='qwerty'):
    '''Тест-07 Быстрое добавление нового питомца без фотографии с буквами в поле возраста.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['age'] is not ''


def test_08_add_new_pet_wo_photo_digi_breed(name='КорГ цифровой породы', animal_type='987654321', age='1'):
    '''Тест-08 Быстрое добавление нового питомца без фотографии с цифрами в поле порода.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] is not ''


def test_09_add_new_pet_without_text_field(name='', animal_type='', age='', pet_photo='images/Relax.jpg'):
    '''Тест-09 Добавление нового питомца с фотографией без заполнения текстовых полей'''

    #Получаем полный путь к файлу с изображением и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['pet_photo'] is not ''


def test_10_add_new_empty_pet(name='', animal_type='', age=''):
    '''Тест-10 Быстрое добавление нового питомца без данных.'''

    #Запрашиваем ключ API и сохраняем в переменную auth_key
    _, auth_key = pf.get_api_key(valid_email, valid_password)

    #Добавляем питомца
    status, result = pf.add_new_pet_wo_photo(auth_key, name, animal_type, age)

    #Сверяем ожидаемый и фактический результат
    assert status == 200
    assert result['name'] == name
    assert result['animal_type'] == animal_type
    assert result['age'] == age
