aria2c --enable-rpc --check-certificate=false \
   --max-connection-per-server=10 --rpc-max-request-size=1024M \
   --bt-stop-timeout=1200 --min-split-size=10M --follow-torrent=mem --split=10 \
   --daemon=true --allow-overwrite=true --max-overall-download-limit=0 \
   --max-overall-upload-limit=1K --max-concurrent-downloads=15 --continue=true \
   --peer-id-prefix=-qB4360- --user-agent=qBittorrent/4.3.6 --peer-agent=qBittorrent/4.3.6 \
   --disk-cache=64M --bt-enable-lpd=true --seed-time=0 --max-file-not-found=0 \
   --max-tries=20 --auto-file-renaming=true --reuse-uri=true --http-accept-gzip=true \
   --content-disposition-default-utf8=true --netrc-path=/usr/src/app/.netrc
