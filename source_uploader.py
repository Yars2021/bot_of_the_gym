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


def get_data(request_data_dict):
    return int(request_data_dict["requester"]), request_data_dict["name"], request_data_dict["request"],\
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
        "outtmpl": os.path.join(
            sources_root,
            sources_dir,
            f"{user_name}_{str(now.year)}{str(now.month)}{str(now.day)}{str(now.hour)}{str(now.minute)}{str(now.second)}.%(ext)s"
        ),
        "preferredcodec": preferred_codec,
    })

    info = ytdl_video.extract_info(request_str, download=True)
    result = ytdl_video.prepare_filename(info)

    ytdl_video.close()

    return result


def upload_file(local_path_str, cloud_path_str, extension):
    disk = yadisk.YaDisk(token=global_vars.YANDEX)

    if not disk.check_token():
        result = "token_fail"
    else:
        if not disk.exists(global_vars.cloud_dir):
            disk.mkdir(global_vars.cloud_dir)

        disk.upload(local_path_str, cloud_path_str, timeout=300.0)
        disk.rename(cloud_path_str, cloud_path_str.split("/")[-1] + extension)

        result = disk.publish(cloud_path_str + extension).get_download_link()

        disk.close()

    return result


def mark_as_uploaded(result: str):
    with open(global_vars.uploaded_files, "r", encoding="utf-8") as f:
        ready_files = list(ast.literal_eval(f.read()))

    f.close()

    ready_files.append({
        "requester": str(user_id),
        "result": result
    })

    with open(global_vars.uploaded_files, "w", encoding="utf-8") as f:
        json.dump(ready_files, f)

    f.close()


print("Вспомогательный процесс-загрузчик запущен")


while True:
    if os.path.exists(global_vars.files_to_upload):
        with open(global_vars.files_to_upload, "r", encoding="utf-8") as f:
            files = list(ast.literal_eval(f.read()))

        f.close()

        if len(files) > 0:
            user_id, user_name, request, sound_only = get_data(files.pop(0))

            with open(global_vars.files_to_upload, "w", encoding="utf-8") as f:
                json.dump(files, f)

            f.close()

            file_path, ext = os.path.splitext(download_file(request, sound_only))

            os.rename(file_path + ext, file_path)

            local_path = os.path.join(sources_root, sources_dir, file_path)
            cloud_path = global_vars.cloud_dir + "/" + (file_path.split("/")[-1]).split(".")[0]

            mark_as_uploaded(upload_file(local_path, cloud_path, ext))
            os.remove(local_path)

        time.sleep(1)
