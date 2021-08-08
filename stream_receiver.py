"""receive frames from the sender"""
import subprocess as sp
import numpy as np
import cv2


class FFmpegReceiver:
    def __init__(self, stream_ip):
        self.ip = stream_ip
        self.rtspUrl = 'rtsp://%s:%d/test' % (self.ip, 8554)
        self.command = [
            'ffmpeg',
            '-f', 'rtsp',  # 强制输入或输出文件格式
            '-rtsp_transport', 'tcp',  # 强制使用 tcp 通信
            '-timeout', '10',  # 设置TCP连接的等待时间
            '-i', self.rtspUrl,  # 输入
            # 're',#
            # '-y', # 无需询问即可覆盖输出文件
            # '-f', 'rawvideo',  # 强制输入或输出文件格式
            '-f', 'image2pipe',  # 强制输出到管道
            '-vcodec', 'rawvideo',  # 设置视频编解码器。这是-codec:v的别名
            '-pix_fmt', 'bgr24',  # 设置像素格式
            '-video_size', '256x256',  # 设置图像尺寸
            '-preset', 'ultrafast',
            '-r', '10',  # 设置帧率
            '-an', '-']
        self.pipe = sp.Popen(self.command, stdout=sp.PIPE)

    def read(self):
        frame = self.pipe.stdout.read(256*256*3)
        if frame is not None:
            frame = np.frombuffer(frame, dtype='uint8')
            return frame.reshape((256, 256, 3))
        else:
            return None

    def receive(self):
        count = 0
        while True:
            frame = self.read()
            if frame is not None:
                print("No. %d: " % count, np.mean(frame))
                count += 1
                cv2.imwrite('temp/%d.jpeg' % count, frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            self.pipe.stdout.flush()


if __name__ == '__main__':
    streamer = FFmpegReceiver('127.0.0.1')
    streamer.receive()
