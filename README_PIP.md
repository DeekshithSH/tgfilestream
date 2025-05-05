# tgfilestream
A Telegram bot that can stream Telegram files to users over HTTP.

## Setup
Install `tgfilestream` package
```
pip install tgfilestream
```
### Optional Extras

- **For environment variables support**:
    ```
    pip install tgfilestream[env]
    ```

- **For fast processing**:
    ```
    pip install tgfilestream[fast]
    ```

- **For all features**:
    ```
    pip install tgfilestream[all]
    ```


Create a text file to store environment variables
example (`secrets.env`):
```
TG_API_ID=1234567
TG_API_HASH=66a73ed2f8a80f52488dfdb3b128bae6
HOST=127.0.0.1
PORT=8080
PUBLIC_URL=http://127.0.0.1:8080
TG_BOT_FATHER_TOKEN=1234567890:b93dcfa3120fa82350e2bc72df83380e
```

Start the bot and server using the following command
```
tgfilestream --env [path to the text file]
```
example:
```
tgfilestream --env secrets.env
```

#### Note
A reverse proxy is recommended to add TLS. When using a reverse proxy, keep
`HOST` as-is, but add the publicly accessible URL to `PUBLIC_URL`. The URL
should include the protocol, e.g. `https://example.com`.

### Environment variables
* `TG_API_ID` (required) - Your Telegram API ID.
* `TG_API_HASH` (required) - Your Telegram API hash.
* `TG_BOT_TOKEN` (required) - Your Telegram Bot Token.
* `TG_SESSION_NAME` (defaults to `tgfilestream`) - The name of the Telethon session file to use.
* `PORT` (defaults to `8080`) - The port to listen at.
* `HOST` (defaults to `localhost`) - The host to listen at.
* `PUBLIC_URL` (defaults to `http://localhost:8080`) - The prefix for links that the bot gives.
* `TRUST_FORWARD_HEADERS` (defaults to false) - Whether or not to trust X-Forwarded-For headers when logging requests.
* `DEBUG` (defaults to false) - Whether or not to enable extra prints.
* `LOG_CONFIG` - Path to a Python basic log config. Overrides `DEBUG`.
* `REQUEST_LIMIT` (default 5) - The maximum number of requests a single IP can have active at a time.
* `CONNECTION_LIMIT` (default 20) - The maximum number of connections to a single Telegram datacenter.
* `CACHE_SIZE` (defaults to 128) - The number of FileInfo objects (messages) to cache.