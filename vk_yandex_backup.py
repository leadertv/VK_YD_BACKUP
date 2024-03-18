import requests
import json
from tqdm import tqdm


# Классные классы. Используем их, для эффективного применения API и концепции ООП для получения высшей оценки
class VKClient:
    """
    Класс для работы с VK API
    В нём мы получаем фотографии профиля пользователя
    Стараюсь использовать Docstring для выработки этой привычки
    """
    API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token):
        self.access_token = access_token

    def get_photos(self, user_id):
        params = {
            'access_token': self.access_token,
            'v': '5.131',
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1,
            'photo_sizes': 1
        }
        response = requests.get(f"{self.API_BASE_URL}photos.get", params=params)
        response.raise_for_status()
        return response.json()['response']['items']


class YandexDiskClient:
    """
    Класс для работы с Яндекс.Диск API
    В нём мы загружаем на Яндекс.Диск фотографии профиля пользователя
    А так-же создаём нужную папку
    """
    API_BASE_URL = 'https://cloud-api.yandex.net/v1/disk/resources'

    def __init__(self, access_token):
        self.access_token = access_token

    def create_folder(self, folder_name):
        headers = {'Authorization': f'OAuth {self.access_token}'}
        params = {'path': folder_name}
        response = requests.put(self.API_BASE_URL, headers=headers, params=params)
        if response.status_code not in (201, 409):
            response.raise_for_status()

    def upload_photo(self, url, path):
        headers = {'Authorization': f'OAuth {self.access_token}'}
        params = {
            'url': url,
            'path': path,
            'overwrite': 'true'
        }
        response = requests.post(f"{self.API_BASE_URL}/upload", headers=headers, params=params)
        response.raise_for_status()


def main(vk_access_token, yandex_access_token, vk_user_id):
    """
    Основная функция в которой происходит уличная магия.
    """
    vk_client = VKClient(vk_access_token)
    yandex_client = YandexDiskClient(yandex_access_token)
    photos = vk_client.get_photos(vk_user_id)

    yandex_folder_name = 'VK_Backup'
    yandex_client.create_folder(yandex_folder_name)

    uploaded_photos = []
    for photo in tqdm(photos[:5], desc="Загрузка фотографий"):
        max_size = max(photo['sizes'], key=lambda size: size['width'] * size['height'])
        photo_url = max_size['url']
        likes = photo['likes']['count']  # Считаем лайки
        upload_date = photo['date']  # Делаем дату загрузки
        file_name = f"{likes}_{upload_date}.jpg"
        path = f"{yandex_folder_name}/{file_name}"
        yandex_client.upload_photo(photo_url, path)
        uploaded_photos.append({'file_name': file_name, 'size': max_size['type']})

    with open('photos_info.json', 'w') as f:
        json.dump(uploaded_photos, f, indent=4)

    # Выводим сообщение об успешной загрузке с использованием цветного текста для красоты.
    print('\n\033[32mБэкап успешно завершён, фотографии были загружены на Яндекс.Диск.\033[0m')


if __name__ == '__main__':
    vk_user_id = input("Введите ID пользователя VK: ")
    vk_access_token = input("Введите токен VK: ")
    yandex_access_token = input("Введите токен Яндекс.Диска: ")
    main(vk_access_token, yandex_access_token, vk_user_id)
