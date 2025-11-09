import json
import secrets
from datetime import datetime, timedelta


def generate_uuid() -> str:
    return secrets.token_hex(8) + "-" + secrets.token_hex(4)


def generate_v2ray_config(
    server_host: str,
    server_port: int,
    uuid: str,
    alter_id: int,
    network: str = "tcp",
    security: str = "auto",
    name: str | None = None,
) -> str:
    config = {
        "v": "2",
        "ps": name or f"VPN-{uuid[:6]}",
        "add": server_host,
        "port": server_port,
        "id": uuid,
        "aid": alter_id,
        "net": network,
        "type": "none",
        "host": "",
        "path": "",
        "tls": security,
    }
    return json.dumps(config, indent=2)


def create_temp_plan(data_gib: int, percentage: float = 0.1) -> int:
    temp_mb = int(data_gib * 1024 * percentage)
    return max(temp_mb, 200)


def build_usage_record(server: dict, data_gib: int, duration_days: int, is_trial: bool = False):
    uuid = generate_uuid()
    config = generate_v2ray_config(
        server_host=server["host"],
        server_port=server["port"],
        uuid=uuid,
        alter_id=server["alter_id"],
        network=server["network"],
        name=server["name"],
    )
    expires_at = datetime.utcnow() + timedelta(days=duration_days)
    quota_mb = data_gib if is_trial else data_gib * 1024
    return config, quota_mb, expires_at
