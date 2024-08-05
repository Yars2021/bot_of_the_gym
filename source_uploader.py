import ast
import datetime
import json
import os
import time
import yadisk
import yt_dlp

from configs import global_vars


sources_root = os.path.join(os.path.dirname(__file__), "./data")
sources_dir = "yt_video_sources"


def shuffle_requests(request_list):
    if len(request_list) <= 0:
        return []
    else:
        requester_dict = {}

        for request_entry in request_list:
            if request_entry["requester"] not in requester_dict:
                requester_dict[request_entry["requester"]] = [request_entry]
            else:
                requester_dict[request_entry["requester"]].append(request_entry)

        shuffled_requests = []

        iterated_users = 1

        while iterated_users > 0:
            for requester in requester_dict:
                iterated_users = 0

                if len(requester_dict[requester]) > 0:
                    shuffled_requests.append(requester_dict[requester].pop(0))
                    iterated_users += 1

                if iterated_users == 0:
                    break

        return shuffled_requests


def get_data(request_data_dict):
    return int(request_data_dict["requester"]), request_data_dict["name"], request_data_dict["request"],\
        request_data_dict["playlist"], request_data_dict["index"],\
        (request_data_dict["format_flag"] == "True")


def download_file(request_str, sound_only_flag):
    global sources_root
    global sources_dir

    now = datetime.datetime.utcnow()

    if sound_only_flag:
        download_format = "bestaudio/best"
        preferred_codec = "mp3"
    else:
        download_format = "bestvideo+bestaudio/best"
        preferred_codec = "mp4"

    ytdl_video = yt_dlp.YoutubeDL({
        "format": download_format,
        "preferredcodec": preferred_codec,
        "outtmpl": os.path.join(
            sources_root,
            sources_dir,
            f"{user_name}_{str(now.year)}{str(now.month)}{str(now.day)}{str(now.hour)}{str(now.minute)}{str(now.second)}.%(ext)s"
        )
    })

    info = ytdl_video.extract_info(request_str, download=True)
    result = ytdl_video.prepare_filename(info)

    ytdl_video.close()

    if "entries" not in info:
        video_data_dict = {
            "title": info["title"],
            "uploader": info["uploader"],
            "description": info["description"],
            "upload_date": info["upload_date"]
        }
    else:
        video_data_dict = {
            "title": info["entries"][0]["title"],
            "uploader": info["entries"][0]["uploader"],
            "description": info["entries"][0]["description"],
            "upload_date": info["entries"][0]["upload_date"]
        }

    return result, video_data_dict


# ToDo make use of this
def cleanup(disk):
    threshold = datetime.datetime.utcnow() - datetime.timedelta(days=7)
    resources = disk.listdir(global_vars.cloud_dir)

    for resource in resources:
        if resource.created < threshold:
            disk.remove(resource.path)


def upload_file(local_path_str, cloud_path_str, title, extension):
    disk = yadisk.YaDisk(token=global_vars.YANDEX)

    if not disk.check_token():
        result = "token_fail"
    else:
        if not disk.exists(global_vars.cloud_dir):
            disk.mkdir(global_vars.cloud_dir)

        final_name = title.replace("/", "|") + extension

        if not disk.exists(global_vars.cloud_dir + "/" + final_name):
            disk.upload(local_path_str, cloud_path_str, timeout=300.0)
            disk.rename(cloud_path_str, final_name)

        result = disk.publish(global_vars.cloud_dir + "/" + final_name).get_download_link()

        disk.close()

    return result


def upload_playlist_part(local_path_str, cloud_playlist_dir, cloud_path_str, title, extension):
    disk = yadisk.YaDisk(token=global_vars.YANDEX)

    if not disk.check_token():
        result = "token_fail"
    else:
        if not disk.exists(global_vars.cloud_dir):
            disk.mkdir(global_vars.cloud_dir)

        playlist_dir_path = global_vars.cloud_dir + "/" + cloud_playlist_dir

        if not disk.exists(playlist_dir_path):
            disk.mkdir(playlist_dir_path)

        final_name = title.replace("/", "|") + extension

        if not disk.exists(playlist_dir_path + "/" + final_name):
            disk.upload(local_path_str, cloud_path_str, timeout=300.0)
            disk.rename(cloud_path_str, final_name)

        result = disk.publish(playlist_dir_path + "/" + final_name).get_download_link()

        disk.close()

    return result


def mark_as_uploaded(video_data_dict, requester_id, public_link):
    with open(global_vars.uploaded_files, "r", encoding="utf-8") as f:
        ready_files = list(ast.literal_eval(f.read()))

    f.close()

    ready_files.append({
        "requester": str(requester_id),
        "result": public_link,
        "title": video_data_dict["title"],
        "uploader": video_data_dict["uploader"],
        "description": video_data_dict["description"],
        "upload_date": video_data_dict["upload_date"]
    })

    with open(global_vars.uploaded_files, "w", encoding="utf-8") as f:
        json.dump(ready_files, f)

    f.close()


def publish_playlist(playlist_path):
    disk = yadisk.YaDisk(token=global_vars.YANDEX)

    if not disk.check_token():
        result = "token_fail"
    else:
        if not disk.exists(playlist_path):
            result = f"path_fail: {playlist_path}"
        else:
            result = disk.publish(playlist_path).get_download_link()

        disk.close()

    return result


def mark_playlist_as_uploaded(requester_id, playlist_title, public_link):
    with open(global_vars.uploaded_files, "r", encoding="utf-8") as f:
        ready_files = list(ast.literal_eval(f.read()))

    f.close()

    ready_files.append({
        "requester": str(requester_id),
        "result": public_link,
        "title": playlist_title,
        "uploader": "",
        "description": "Плейлист загружен",
        "upload_date": ""
    })

    with open(global_vars.uploaded_files, "w", encoding="utf-8") as f:
        json.dump(ready_files, f)

    f.close()


print("Вспомогательный процесс-загрузчик запущен")


while True:
    if os.path.exists(global_vars.files_to_upload):
        with open(global_vars.files_to_upload, "r", encoding="utf-8") as f:
            files = shuffle_requests(list(ast.literal_eval(f.read())))

        f.close()

        if len(files) > 0:
            user_id, user_name, request, playlist, index, sound_only = get_data(files.pop(0))
            playlist = playlist.replace("/", "|").replace(" ", "_")

            with open(global_vars.files_to_upload, "w", encoding="utf-8") as f:
                json.dump(files, f)

            f.close()

            filename, video_data = download_file(request, sound_only)
            file_path, ext = os.path.splitext(filename)

            os.rename(file_path + ext, file_path)

            local_path = os.path.join(sources_root, sources_dir, file_path)

            if playlist == "":
                cloud_path = global_vars.cloud_dir + "/" + (file_path.split("/")[-1]).split(".")[0]
                mark_as_uploaded(video_data, user_id, upload_file(local_path, cloud_path, video_data["title"], ext))
            else:
                cloud_path = global_vars.cloud_dir + "/" + playlist + "/" + (file_path.split("/")[-1]).split(".")[0]
                upload_playlist_part(local_path, playlist, cloud_path, video_data["title"], ext)

                if index == "1":
                    playlist_cloud_path = global_vars.cloud_dir + "/" + playlist
                    mark_playlist_as_uploaded(user_id, playlist, publish_playlist(playlist_cloud_path))

            os.remove(local_path)

        time.sleep(1)
