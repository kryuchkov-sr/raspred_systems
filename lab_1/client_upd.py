import grpc
import music_player_pb2
import music_player_pb2_grpc

def list_playlists(stub):
    """
    Запрашивает список плейлистов и выводит их.
    """
    print("\n--- Получаем список плейлистов ---")
    response = stub.GetPlaylistsList(music_player_pb2.Empty())

    playlists = []
    for playlist in response.playlists:
        print(f"ID: {playlist.id} | Название: {playlist.name}")
        playlists.append(playlist.id)

    return playlists

def stream_playlist(stub, playlist_id):
    """
    Запрашивает треки из выбранного плейлиста и выводит их.
    """
    print(f"\n--- Запрашиваем плейлист: {playlist_id} ---")
    playlist_request = music_player_pb2.PlaylistRequest(playlist_id=playlist_id)

    try:
        track_stream = stub.StreamPlaylist(playlist_request)
        for track_response in track_stream:
            print("\n--- Получен новый трек ---")
            print(f"ID трека: {track_response.track_id}")
            print(f"Название:  {track_response.title}")
            print(f"Исполнитель: {track_response.artist}")
            print(f"Альбом: {track_response.album}")
            print(f"Размер чанка (байт): {len(track_response.audio_chunk)}")

        print("\nВесь плейлист получен!")

    except grpc.RpcError as e:
        print(f"Ошибка RPC: {e.code()} -> {e.details()}")

def run():
    """
    Функция для тестирования клиента.
    """
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = music_player_pb2_grpc.CepsucMusicPlayerStub(channel)

        # Получаем список плейлистов
        playlists = list_playlists(stub)

        if not playlists:
            print("Нет доступных плейлистов.")
            return

        # Пользователь выбирает плейлист
        print("\nВыберите ID плейлиста для прослушивания:")
        for pid in playlists:
            print(f"  - {pid}")

        selected = input("\nВведите ID плейлиста: ").strip()

        if selected in playlists:
            stream_playlist(stub, selected)
        else:
            print("Неверный ID плейлиста.")


if __name__ == '__main__':

    run()
