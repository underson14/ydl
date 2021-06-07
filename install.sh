sudo curl -L https://yt-dl.org/downloads/latest/youtube-dl -o /usr/local/bin/youtube-dl
sudo chmod a+rx /usr/local/bin/youtube-dl
apt install -y atomicparsley
git clone https://github.com/underson14/colab-ffmpeg-cuda.git
cp -r ./colab-ffmpeg-cuda/bin/. /usr/bin/
apt install axel -y
apt autoremove
chmod +x "/content/ydl/downvideo.sh"
chmod +x "/content/ydl/downmp3.sh"
pip3 install tidal-dl --upgrade
