FROM anasty17/megasdk:latest

WORKDIR /usr/src/app
RUN chmod 777 /usr/src/app

RUN apt-get install -y wget xz-utils neofetch unzip && apt-get autoremove -y

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

COPY extract /usr/local/bin
COPY pextract /usr/local/bin
RUN chmod +x /usr/local/bin/extract && chmod +x /usr/local/bin/pextract
COPY . .
COPY .netrc /root/.netrc
RUN chmod 600 /usr/src/app/.netrc
RUN chmod +x aria.sh

CMD ["bash","start.sh"]
