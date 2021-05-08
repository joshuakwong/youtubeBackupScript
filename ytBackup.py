#!/usr/bin/env python3

from pytube import YouTube, Playlist
from datetime import datetime
import urllib
import time
import os
import subprocess
import signal

THRESHOLD = 150

def main():
    print('running')
    global scriptStart
    scriptStart = int(time.time())
    playlistLink = "https://www.youtube.com/playlist?list=PLetg744TF10BrdPjaEXf4EsJ1wz6fyf95"
    playlist = Playlist(playlistLink)
    faillist = []
    numVid = len(playlist.video_urls)
    count = 1
    try:
        downloaded = open("./output/"+playlist.title+".txt", "r")
        existing = [line.rstrip() for line in downloaded.readlines()]
        downloaded.close()
    except IOError:
        existing = []
        pass
    downloaded = open("./output/"+playlist.title+".txt", "a")
    global videoStart
    videoStart = 0
    pid = os.getpid()

    for link in playlist:
        try:
            ytVid = YouTube(link)
            pubDate = ytVid.publish_date.strftime("%Y-%m-%d")
            title = ytVid.title
            print("downloading video {}/{} - title: {}".format(count, numVid, ytVid.title))
            ytVid.register_on_progress_callback(progCheck)
            videoStart = int(time.time())
            ytVid.streams.get_highest_resolution().download(output_path="./output", filename_prefix=pubDate, max_retries=5)
            if link not in existing:
                downloaded.write(link+"\n")
            count += 1
        except KeyboardInterrupt:
            faillist.append(link)
            print(">>>>>btw the pid is {} in case you want to kill this proc".format(pid))
            continue
        except Exception as e:
            faillist.append(link)
            continue

    while len(faillist) != 0:
        link = faillist.pop(0)
        try:
            ytVid = YouTube(link)
            pubDate = ytVid.publish_date.strftime("%Y-%m-%d")
            title = ytVid.title
            print("downloading video {}/{} - title: {}".format(count, numVid, ytVid.title))
            ytVid.register_on_progress_callback(progCheck)
            videoStart = int(time.time())
            ytVid.streams.get_highest_resolution().download(output_path="./output", filename_prefix=pubDate, max_retries=5)
            if link not in existing:
                downloaded.write(link+"\n")
            count += 1
        except KeyboardInterrupt:
            faillist.append(link)
            print(">>>>>btw the pid is {} in case you want to kill this proc".format(pid))
            continue
        except Exception as e:
            faillist.append(link)
            continue


def progCheck(stream, chunk, remain):
    total = stream.filesize
    downloaded = total - remain
    prog = (int)((downloaded/total)*100)
    now = int(time.time())
    totalLapse = now - scriptStart
    videoLapse = now - videoStart
    if videoLapse > THRESHOLD:
        pid = os.getpid()
        print("\n>>>>>taking way too long, skipping for now...")
        print(">>>>>btw the pid is {} in case you want to kill this proc".format(pid))
        os.kill(pid, signal.SIGINT)

    if prog == 100:
        print("\rprogress: {}%; total lapse: {}s; video lapse: {}s\n".format(prog, totalLapse, videoLapse), end="")
    else:
        print("\rprogress: {}%; total lapse: {}s; video lapse: {}s".format(prog, totalLapse, videoLapse), end="")


if __name__ == "__main__":
    main()
