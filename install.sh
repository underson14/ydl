wget https://yt-dl.org/downloads/latest/youtube-dl -O /usr/local/bin/youtube-dl
chmod a+rx /usr/local/bin/youtube-dl
apt install -y atomicparsley
apt install -y ffmpeg
apt install axel -y
apt autoremove
chmod +x "/content/ydl/downvideo.sh"
chmod +x "/content/ydl/downmp3.sh"
pip3 install tidal-dl --upgrade
