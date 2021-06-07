time youtube-dl --autonumber-start 1 -ci --hls-prefer-native \
--add-metadata --embed-thumbnail -f \
'bestvideo[height<=?1080][fps<=?30][vcodec!=?vp9]+bestaudio[ext=m4a]/best' \
-o "${1}/%(autonumber)s.%(title)s.%(ext)s" $2

