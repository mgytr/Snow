import sys
import random
from PyQt5.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt5.QtGui import QPixmap, QPainter, QImage
from PyQt5.QtCore import Qt, QTimer
from PIL import Image, ImageDraw, ImageFilter
import typing
from pynput import mouse
import threading
import os
import time
def wait_until(condition: callable, timeout=3):
    start = time.time()
    while not condition() and time.time() - start < timeout:
        time.sleep(0.05)
class Snowflake:
    def __init__(self, x, y, size, speed, transparency: int, color: tuple):
        self.x = x
        self.y = y
        self.size = int(size * 1.5)
        self.speed = speed * 1.2
        self.transparency = transparency
        self.color = color
        self.im: Image.Image = Image.open(f'{random.randint(1, 3)}.png').convert('RGBA').resize((int(self.size/1.3), int(self.size/1.3))) if random.choice([False, False, False, True]) else None
        if not self.im:
            self.im = Image.new('RGBA', (self.size, self.size), (0, 0, 0, 0))
            imdraw = ImageDraw.Draw(self.im)
            imdraw.ellipse((3, 3, self.size - 3, self.size - 3), fill=(self.color[0], self.color[1], self.color[2], min(int(self.transparency*1.3), 255)))
            self.im = self.im.filter(ImageFilter.GaussianBlur(3))
        else:
            for y_ in range(self.im.height):
                for x_ in range(self.im.width):
                    pixel = list(self.im.getpixel((x_, y_)))
                    pixel[0] = self.color[0]
                    pixel[1] = self.color[1]
                    pixel[2] = self.color[2]
                    pixel[3] += min(self.transparency - pixel[3], 0)
                    self.im.putpixel((x_, y_), tuple(pixel))

                    
        
    

    def fall(self):
        self.y += self.speed
        if self.y > height - taskbar_height:
            self.y = -self.size
            self.x = random.randint(0, width)
def prime(n): return not any(n % i == 0 for i in range(2,n))
class TransparentOverlay(QLabel):
    def __init__(self, num_snowflakes):
        super().__init__()
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool | Qt.WindowTransparentForInput)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_NoSystemBackground)
        self.showFullScreen()
        self.lastclick = 0
        self.detectingdouble = False
        self.snowflakes = [Snowflake(random.randint(0, width), random.randint(0, height), random.randint(10, 16), random.uniform(2, 4), random.randint(200, 240), 
                                     (
                                         225 if prime(n) else random.randint(240, 255),
                                         random.randint(230, 250) if prime(n) else random.randint(240, 255),
                                         225 if prime(n) else random.randint(240, 255)
                                    ))
                                      for n in range(num_snowflakes)]
        self.accumulated_snow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.snow_heights = [0] * width  # Track snow height at each x-coordinate
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.loop)
        self.timer.start(80)
        self.clickthrough = True
        self.firsttime = True
        self.fallenpos = []
    def paintEvent(self, event):
        if self.pixmap() is not None:
            painter = QPainter(self)
            painter.drawPixmap(self.rect(), self.pixmap())
    def closeEvent(self, event):
        QApplication.instance().quit()
    def reset_snow(self):
        self.fallenpos = []
        self.accumulated_snow = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        self.snow_heights = [0] * width
    def closeEvent(self, event):
        QApplication.instance().quit()
    def on_click(self, x, y, button, pressed):
        #print(x, y)
        
        if not (not pressed and button == mouse.Button.right):
            return
        onsnow = False
        for el in self.fallenpos:
            if (x >= el[0] and x <= el[2]) and (y >= el[1] and y <= el[3]):
                onsnow = True
                break
        if not onsnow:
            return
        
        if not self.detectingdouble:
            def detect(self: TransparentOverlay):
                self.detectingdouble = True
                firstclick = time.time()
                self.lastclick = 0
                
                wait_until(lambda: not self.detectingdouble, 1.4)
                print(time.time()-firstclick)
                
                if self.detectingdouble:
                    self.reset_snow()
                elif self.lastclick-firstclick <= 1.4:
                    os._exit(0)
                    
                self.detectingdouble = False
            threading.Thread(target=detect, args=(self,)).start()
                



        else:
            self.detectingdouble = False
            self.lastclick = time.time()
            return

            
        
    def loop(self):
        if self.firsttime:
            self.firsttime = False

            lis = mouse.Listener(on_click=self.on_click)
            lis.daemon = True
            lis.start()
        im = Image.new('RGBA', (self.rect().width(), self.rect().height()), (0, 0, 0, 0))
        
        for snowflake in self.snowflakes:
            snowflake.fall()
            try:
                if snowflake.y + snowflake.size >= height - taskbar_height - self.snow_heights[int(snowflake.x)]:
                    # Check if there is snow beneath the falling snowflake within its width range
                    for i in range(int(snowflake.x), int(snowflake.x + snowflake.size)):
                        if i < width and self.snow_heights[i] > 0:
                            snowflake.y = (height - taskbar_height - self.snow_heights[i] - snowflake.size)+int(snowflake.im.height/1.8)
                            break
                    
                    # Accumulate snow at the taskbar's top edge
                    circle_im = snowflake.im
                    self.accumulated_snow.paste(circle_im, (int(snowflake.x), int(snowflake.y)), circle_im)
                    for i in range(int(snowflake.x), int(snowflake.x + snowflake.size)):
                        if i < width:
                            self.snow_heights[i] += circle_im.size[1] # Increase the snow height at this x-coordinate
                    self.fallenpos.append((int(snowflake.x), int(snowflake.y), int(snowflake.x+snowflake.size), int(snowflake.y+snowflake.size)))
                    snowflake.y = -snowflake.size
                    snowflake.x = random.randint(0, width)

                else:
                    circle_im = snowflake.im
                    im.paste(circle_im, (int(snowflake.x), int(snowflake.y)), circle_im)
            except IndexError:
                pass
        # Combine the falling snow with the accumulated snow
        im.paste(self.accumulated_snow, (0, 0), self.accumulated_snow)
        data = im.tobytes("raw", "RGBA")
        qimage = QImage(data, im.width, im.height, QImage.Format_RGBA8888)
        self.show()
        self.setPixmap(QPixmap.fromImage(qimage))
def findMainWindow() -> typing.Union[QMainWindow, None]:
    # Global function to find the (open) QMainWindow in application
    app = QApplication.instance()
    for widget in app.topLevelWidgets():
        if isinstance(widget, QMainWindow):
            return widget
    return None
if __name__ == "__main__":
    app = QApplication(sys.argv)
    screen = app.primaryScreen()
    size = screen.size()
    width, height = size.width(), size.height()
    dw = app.desktop()  # dw = QDesktopWidget() also works if app is created
    # Detect taskbar height
    taskbar_height = dw.screenGeometry().height() - dw.availableGeometry().height()
    overlay = TransparentOverlay(num_snowflakes=20)
    sys.exit(app.exec_())
