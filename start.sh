gunicorn wserver:start_server --bind 0.0.0.0:$PORT --worker-class aiohttp.GunicornWebWorker & qbittorrent-nox -d  & ./aria.sh; python3 -m bot 
