export MAX_DOWNLOAD_SPEED=0
tracker_list=$(curl -Ns https://raw.githubusercontent.com/XIU2/TrackersListCollection/master/all.txt https://ngosang.github.io/trackerslist/trackers_all_http.txt https://newtrackon.com/api/all https://raw.githubusercontent.com/DeSireFire/animeTrackerList/master/AT_all.txt https://raw.githubusercontent.com/hezhijie0327/Trackerslist/main/trackerslist_tracker.txt https://raw.githubusercontent.com/hezhijie0327/Trackerslist/main/trackerslist_exclude.txt | awk '$0' | tr '\n' ',')
export MAX_CONCURRENT_DOWNLOADS=7

aria2c --enable-rpc --rpc-listen-all=false --check-certificate=false \
   --max-connection-per-server=10 --rpc-max-request-size=1024M \
   --bt-tracker="[$tracker_list]" --bt-max-peers=0 --bt-tracker-connect-timeout=300 --bt-stop-timeout=1200 --min-split-size=10M \
   --follow-torrent=mem --split=10 \
   --daemon=true --allow-overwrite=true --max-overall-download-limit=$MAX_DOWNLOAD_SPEED \
   --max-overall-upload-limit=1K --max-concurrent-downloads=$MAX_CONCURRENT_DOWNLOADS \
   --peer-id-prefix=-qB4360- --user-agent=qBittorrent/4.3.6 --peer-agent=qBittorrent/4.3.6 \
   --disk-cache=64M --file-allocation=prealloc --continue=true \
   --max-file-not-found=0 --max-tries=20 --auto-file-renaming=true \
   --bt-enable-lpd=true --seed-time=0.01 --seed-ratio=1.0 \
   --content-disposition-default-utf8=true --http-accept-gzip=true --reuse-uri=true --netrc-path=/usr/src/app/.netrc
