wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl
apt-get install -y atomicparsley
apt-get install -y ffmpeg
apt autoremove
chmod +x "/content/ydl/downvideo.sh"
chmod +x "/content/ydl/downmp3.sh"
pip3 install tidal-dl --upgrade
