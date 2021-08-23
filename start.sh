gunicorn wserver:start_server --bind 0.0.0.0:$PORT --worker-class aiohttp.GunicornWebWorker & qbittorrent-nox -d --webui-port=8090 & ./aria.sh; python3 -m bot 
