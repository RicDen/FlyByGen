import logging

class SetUp:
    def __init__(self):
        logging.info(f"Starting SetUp...")        

    def check_libraries(self):
        try:
            import psutil
            import cv2
            import PIL
            # TODO: Add numpy to conda environment
            # import numpy
            logging.info(f"Loaded python libraries  successfully")
        except:
            logging.error(f"Failed to load. Installing python libraries...")
            try:
                import pip
                pip.main(['install', 'psutil'])
                import psutil
                logging.warning("Loaded psutil after install.")
            except Exception as e:
                logging.error(f"Failed to install and load psutil: {e}")
            try:
                import pip
                pip.main(['install', 'opencv-python'])
                import cv2
                logging.warning("Loaded cv2 after install.")
            except Exception as e:
                logging.error(f"Failed to install and load cv2: {e}")
            try:
                import pip
                pip.main(['install', 'pillow'])
                import cv2
                logging.warning("Loaded PIL after install.")
            except Exception as e:
                logging.error(f"Failed to install and load PIL: {e}")