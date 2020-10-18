import os
from robot.libraries.BuiltIn import BuiltIn
from selenium import webdriver
from threading import Thread
from glob import glob 
from time import sleep
import ffmpeg

ROBOT = BuiltIn()


class recording:
    ROBOT_LIBRARY_SCOPE = 'GLOBAL'

    FRAMES_PER_SEC = 5
    PLAYRATE = 2  # ~ 1/speed 

    def create_recording_webdriver(self, *args, **kwargs):
        ROBOT.run_keyword("Create Webdriver", *args, **kwargs)       
        # self.driver = webdriver.Chrome()  # add args, kwargs
        selenium = ROBOT.get_library_instance("Selenium2Library")
        self.driver = selenium._drivers.current
        self.test_name = ROBOT.get_variable_value("${TEST_NAME}").replace(" ", "_")
        self.start_recording()

    def close_recording_browser(self):
        self.stop_recording()
        ROBOT.run_keyword("Close Browser")
        self.video_thread.join()

    def start_recording(self):
        # ROBOT.log_to_console(f"Recording would start for {self.test_name}")
        self.recording = True
        self.thread = Thread(target=self.record)
        self.moment_threads = []
        self.thread.start()

    def stop_recording(self):
        ROBOT.log_to_console(f"Recording would stop for {self.test_name}")
        self.recording = False
        for thread in self.moment_threads:
            thread.join()
        self.video_thread = Thread(target=self.create_video)
        self.video_thread.start()

    def record(self):
        ROBOT.log_to_console(f"Recording thread launched for {self.test_name}")
        frame = 0

        while self.recording:
            moment_thread = Thread(target=self.screenshot, args=(frame,))
            self.moment_threads.append(moment_thread)
            moment_thread.start()
            sleep(1/self.FRAMES_PER_SEC)
            frame += 1

    def screenshot(self, frame_id):
        with open(f'{self.test_name}_%05d.png' % frame_id, 'wb') as f:
            f.write(self.driver.get_screenshot_as_png())

    def create_video(self):
        (ffmpeg
            .input(f'{self.test_name}_*.png', pattern_type="glob", framerate=self.FRAMES_PER_SEC / self.PLAYRATE)
            .output(f'{self.test_name}.mp4')
            .run()
        )
        for png in glob(f'{self.test_name}_*.png'):
            os.unlink(png)

