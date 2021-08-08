"""H.264 Streaming methods"""
import numpy as np
import subprocess as sp
import time
import cv2
# from imageio import get_reader


class FrameGenerator:
    """
generate a frame of random gray scale
    """

    def __init__(self, size, source=None):
        self.size = size
        self.count = 0
        self.source = source
        if self.source is not None:
            self.cap = cv2.VideoCapture(self.source)
            if not self.cap.isOpened():
                print('Video not available.')
                self.source = None

    def generate(self):
        """
    generate a frame
        :return:
        """
        frame_gray = np.random.randint(0, 255) * np.ones(self.size).astype('uint8')
        if self.source is None:
            return frame_gray
        else:
            ret, frame = self.cap.read()
            if ret:
                return frame
            else:
                self.cap = cv2.VideoCapture(self.source)
                return self.generate()


class FFmpegStreamer:
    def __init__(self, target_ip, target_port=8554, fps=25, frame_size=256, rate=20):
        self.frame_generator = FrameGenerator((256, 256, 3), source='test_video_cropped.mp4')
        self.target_ip = target_ip
        self.target_port = target_port
        self.fps = fps
        self.frame_size = frame_size
        self.size_str = '%dx%d' % (self.frame_size, self.frame_size)
        self.rate = rate  # kbps
        self.rtspUrl = 'rtsp://%s:%d/test' % (self.target_ip, self.target_port)
        # written according to https://www.cnblogs.com/Manuel/p/15006727.html
        self.command = [
            'ffmpeg',
            # 're',#
            # '-y', # 无需询问即可覆盖输出文件
            '-f', 'rawvideo',  # 强制输入或输出文件格式
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-s', self.size_str,  # 设置图像大小
            '-r', str(fps),  # 设置帧率
            '-i', '-',  # 输入
            '-timeout', '10',  # 设置TCP连接的等待时间
            '-b:v', '%dk' % self.rate,  # 设置数据率
            '-c:v', 'libx264',
            # '-x264opts', 'bitrate=%d' % self.rate,  # 设置比特率（kbps）
            '-pix_fmt', 'bgr24',
            '-preset', 'ultrafast',
            '-f', 'rtsp',  # 强制输入或输出文件格式
            # '-rtsp_transport', 'udp',  # 使用UDP推流
            '-rtsp_transport', 'tcp',  # 使用TCP推流
            self.rtspUrl]
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)
        self.count = 0

    def set_rate(self, rate):
        self.rate = rate
        self.command[10] = '%dk' % self.rate
        self.pipe = sp.Popen(self.command, stdin=sp.PIPE)

    def stream(self):
        frame = self.frame_generator.generate()
        self.pipe.stdin.write(frame.tostring())
        self.count += 1
        print('No. %d: ' % self.count, np.mean(frame))


if __name__ == '__main__':
    streamer = FFmpegStreamer('166.111.224.29', fps=10, rate=5)
    while True:
        streamer.stream()
        time.sleep(1/10)
