import os
import shutil
import zipfile

from django.conf import settings
from django.http import HttpResponse, Http404


def get_file_list(path):
    """returns a list of agent files"""
    d = {"name": os.path.basename(path)}
    if os.path.isdir(path):
        d["type"] = "directory"
        d["children"] = [
            get_file_list(os.path.join(path, x)) for x in os.listdir(path)
        ]
    else:
        d["type"] = "file"
    return d


def save_agent_files(agent_id, upload):
    """create agent directory and save uploaded agent files to disk, decompressing the zip file"""
    path = os.path.join(settings.DIR_AGENTS, str(agent_id))
    os.makedirs(path)
    if upload is not None:
        with zipfile.ZipFile(upload.file) as zip_ref:
            zip_ref.extractall(path)


def load_agent_files(agent_id):
    """load agent files as zip and return an HTTPResponse for download"""
    os.makedirs(settings.DIR_TEMP, exist_ok=True)
    os.makedirs(settings.DIR_AGENTS, exist_ok=True)

    agent_path = os.path.join(settings.DIR_AGENTS, str(agent_id))
    zip_path = os.path.join(settings.DIR_TEMP, str(agent_id))

    os_path = f"{zip_path}.zip"

    if not os.path.exists(os_path):
        shutil.make_archive(zip_path, "zip", agent_path)

    if os.path.exists(os_path):
        with open(os_path, "rb") as fh:
            response = HttpResponse(
                fh.read(), content_type="application/force-download"
            )
            response[
                "Content-Disposition"
            ] = "attachment; filename=" + os.path.basename(os_path)
            os.remove(os_path)
            return response
    raise Http404


def delete_agent_files(filename):
    """remove all agent files"""
    path = os.path.join(settings.DIR_AGENTS, str(filename))
    if os.path.exists(path):
        shutil.rmtree(path)
