import json
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
MODELS_DIR = PROJECT_ROOT / "models"
CONFIG_DIR = PROJECT_ROOT / "config"
DATA_DIR = PROJECT_ROOT / "data"
CONFIG_FILE = CONFIG_DIR / "config.json"
EXPORT_DIR = PROJECT_ROOT / "export"

def load_config(config_path=None):
    """
    从 config.json 读取配置并返回字典。

    参数
    ----------
    config_path : str or Path, optional
        配置文件路径，默认为 config/config.json。

    返回
    ----------
    dict
        包含 username, password, courses 的字典。
        courses 是一个列表，每项为 {"name": str, "url": str}。
    """
    if config_path is None:
        config_path = CONFIG_FILE

    with open(config_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data


def get_account(config_path=None):
    """读取配置中的 username"""
    data=load_config(config_path)
    accountinfo=[data["username"],data["password"]]
    return accountinfo


def get_courses(config_path=None):
    """读取配置中的 courses 列表，每项 {"name": str, "url": str}"""
    return load_config(config_path)["courses"]


API_FILE = CONFIG_DIR / "api.json"


def get_apis(api_path=None):
    """
    从 api.json 读取 API 配置，返回列表，每项为 {"apikey": str, "url": str, "model": str}。
    """
    if api_path is None:
        api_path = API_FILE

    with open(api_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    return data
