youtube-dl -cio '/content/drive/My Drive/youtube-dl/Videos/%(title)s.%(ext)s' --hls-prefer-native --add-metadata --write-auto-sub  --embed-thumbnail -f 'bestvideo[height<=?1080][fps<=?30][vcodec!=?vp9]+bestaudio[ext=m4a]/best' $1
