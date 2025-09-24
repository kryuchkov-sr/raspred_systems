import grpc
import music_player_pb2
import music_player_pb2_grpc

def run():
    """
    Функция для тестирования клиента.
    """
    # Открываем канал связи с сервером на localhost и порту 50051
    with grpc.insecure_channel('localhost:50051') as channel:
        # Создаем заглушку (Stub) - это объект, через который мы вызываем удаленные методы.
        stub = music_player_pb2_grpc.CepsucMusicPlayerStub(channel)

        # Создаем запрос с ID плейлиста
        playlist_request = music_player_pb2.PlaylistRequest(playlist_id="summer_hits")

        print(f"Клиент запрашивает плейлист: {playlist_request.playlist_id}")

        try:
            # Вызываем удаленный метод StreamPlaylist.
            # Так как это серверный стриминг, мы получаем не один ответ, а поток (итератор) ответов.
            track_stream = stub.StreamPlaylist(playlist_request)

            # Итерируемся по потоку треков, которые отправляет сервер
            for track_response in track_stream:
                print("\n--- Получен новый трек ---")
                print(f"ID трека: {track_response.track_id}")
                print(f"Название:  {track_response.title}")
                print(f"Исполнитель: {track_response.artist}")
                print(f"Альбом: {track_response.album}")
                print(f"Размер чанка (байт): {len(track_response.audio_chunk)}")

            print("\nВесь плейлист получен!")

        except grpc.RpcError as e:
            # Обрабатываем ошибки, которые мог установить сервер (например, NOT_FOUND)
            print(f"Ошибка RPC: {e.code()} -> {e.details()}")

if name == '__main__':
    run()