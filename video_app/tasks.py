import subprocess

def convert_480p(source):
    target = source + "_480p.mp4"
    cmd = "ffmpeg -i {} -vf scale=-2:480 {}".format(source, target)
    subprocess.run(cmd)