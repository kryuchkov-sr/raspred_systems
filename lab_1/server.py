import grpc
from concurrent import futures
import time
import music_player_pb2
import music_player_pb2_grpc

# Наследуемся от сгенерированного класса Servicer
class CepsucMusicPlayerServicer(music_player_pb2_grpc.CepsucMusicPlayerServicer):
    """
    Реализация сервиса CepsucMusicPlayer.
    """

    # Реализуем метод StreamPlaylist
    def StreamPlaylist(self, request, context):
        """
        Реализация RPC-метода StreamPlaylist.
        request: Объект типа PlaylistRequest, присланный клиентом.
        context: Контекст RPC, позволяет, среди прочего, обрабатывать прерывания.
        """

        # Просто для демонстрации: выводим полученный ID
        print(f"Запрос на стриминг плейлиста с ID: {request.playlist_id}")

        # Имитируем базу данных плейлистов.
        # В реальности здесь был бы запрос к БД или файловой системе.
        playlist_library = {
            "summer_hits": [
                {"id": "id_1", "title": "Lucid Dreams", "artist": "Juice WRLD", "album": "Goodbye & Good Riddance"},
                {"id": "id_2", "title": "Ransom", "artist": "Lil Tecca, Juice WRLD", "album": "We Love You Tecca"},
                {"id": "id_3", "title": "Батареи", "artist": "Нервы", "album": "Всё Что Вокруг"},
                {"id": "id_4", "title": "Как на войне", "artist": "Агата Кристи", "album": "Избранное"},
                {"id": "id_5", "title": "Graf Monte-Cristo", "artist": "FRIENDLY THUG 52 NGG", "album": "Graf Monte-Cristo / Most Valuable Pirate"},
                {"id": "id_6", "title": "Прощание", "artist": "Три дня дождя, MONA", "album": "melancholia"},
            ]
        }

        # Получаем плейлист по ID из запроса. Если нет такого - возвращаем пустой список.
        tracks_data = playlist_library.get(request.playlist_id, [])

        # Проверяем, нашли ли мы плейлист
        if not tracks_data:
            # Устанавливаем статус ошибки для клиента
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details(f"Плейлист с ID '{request.playlist_id}' не найден.")
            # Поскольку это потоковая передача, мы просто не будем ничего отправлять.
            # Можно также сгенерировать исключение.
            return

        # Итерируемся по списку треков в найденном плейлисте
        for track_info in tracks_data:
            # Создаем сообщение TrackResponse для каждого трека
            track_response = music_player_pb2.TrackResponse(
                track_id=track_info["id"],
                title=track_info["title"],
                artist=track_info["artist"],
                album=track_info["album"],
                audio_chunk=b"fake_audio_data_chunk" # Имитация аудио-чанка
            )

            # Используем yield, чтобы отправить трек и приостановить выполнение,
            # пока не будет готов следующий. Это ключевой момент стриминга.
            print(f"Отправляю трек: {track_info['title']}")
            yield track_response

            # Имитация задержки (например, чтения с диска или сетевой задержки)
            time.sleep(2)

        # После цикла метод завершается, что сигнализирует об окончании потока.
        print("Стриминг плейлиста завершен.")


def serve():
    """
    Функция для запуска gRPC-сервера.
    """
    # Создаем сервер с пулом потоков
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # Добавляем наш реализованный сервис к серверу
    music_player_pb2_grpc.add_CepsucMusicPlayerServicer_to_server(
        CepsucMusicPlayerServicer(), server
    )

    # Слушаем порт 50051
    server.add_insecure_port('[::]:50051')
    server.start() # Сервер запускается в фоновых потоках
    print("Сервер запущен на порту 50051...")

    # Блокируем основной поток, чтобы сервер не завершился сразу
    try:
        while True:
            time.sleep(86400) # Ожидаем сутки (или до прерывания Ctrl+C)
    except KeyboardInterrupt:
        server.stop(0) # Корректно останавливаем сервер при нажатии Ctrl+C


if name == '__main__':
    serve()