import requests

from decouple import config

# Замените это на ваш API ключ Amplitude
api_key = config("API_KEY")


def send_registration_event_to_amplitude(device_id, event_type):
    try:
        # Данные события регистрации
        event_data = {
            "api_key": api_key,
            "events": [
                {
                    "device_id": device_id,  # Ваш идентификатор устройства или пользователя
                    "event_type": event_type,  # Тип события, например, "Sign up"
                }
            ],
        }

        # URL для отправки события в Amplitude
        url = "https://api2.amplitude.com/2/httpapi"

        # Отправляем событие
        response = requests.post(
            url, json=event_data, headers={"Content-Type": "application/json"}
        )

        # Проверяем ответ
        if response.status_code == 200:
            print(f"Событие регистрации успешно отправлено в Amplitude.")
        else:
            print(
                f"Ошибка при отправке события регистрации в Amplitude: {response.status_code}"
            )
            print(response.text)
    except Exception as e:
        print(f"Ошибка при отправке события регистрации в Amplitude: {str(e)}")
