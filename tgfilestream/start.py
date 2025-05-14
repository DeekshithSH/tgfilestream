import argparse
import os

def main():
    parser = argparse.ArgumentParser(description="A Telegram bot that can stream Telegram files to users over HTTP.")
    parser.add_argument("--api-id", type=int, help="Your Telegram API ID")
    parser.add_argument("--api-hash", type=str, help="Your Telegram API Hash")
    parser.add_argument("--bot-token", type=str, help="Your Telegram Bot Token")
    parser.add_argument("--env", type=str, default=".env", help="Path to the environment file (default: .env)")
    parser.add_argument("--host", type=str, help="Override the host address")
    parser.add_argument("--port", type=int, help="Override the port number")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    args = parser.parse_args()

    arg_to_env = {
        "env": "ENV_PATH",
        "api_id": "TG_API_ID",
        "api_hash": "TG_API_HASH",
        "bot_token": "TG_BOT_TOKEN",
        "host": "HOST",
        "port": "PORT",
        "debug": "DEBUG",
    }

    # Set only the provided args
    for arg_key, env_key in arg_to_env.items():
        value = getattr(args, arg_key)
        if value is not None:
            os.environ[env_key] = str(value)

    import tgfilestream.__main__
