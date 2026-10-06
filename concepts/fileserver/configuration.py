import json
from dataclasses import dataclass

"""
{
    "server": {
        "index": bool,
        "port": int,
        "bind_addr": str,
        "backlog": int,
        "root": str,
    }
}
"""

CONFIG_PATH = "./config"


@dataclass
class ServerConfig:
    index: bool
    port: int
    bind_addr: str
    backlog: int
    root: str


# Read and initialize configuration.
def init_config() -> ServerConfig:
    with open(CONFIG_PATH, "r") as file:
        configurations = json.load(file)
    server_config = configurations.get("server", None)
    if not isinstance(server_config, dict):
        raise ValueError(
            "Invalid configuration file." "Please follow the standard format"
        )
    return ServerConfig(
        index=server_config.get("index", "false"),
        port=server_config.get("port", 8080),
        root=server_config.get("root", "./content"),
        backlog=server_config.get("backlog", 10),
        bind_addr=server_config.get("bind_addr", "127.0.0.1"),
    )
