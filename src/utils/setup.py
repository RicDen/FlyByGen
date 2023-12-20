import logging

class SetUp:
    def __init__(self):
        logging.info(f"Starting SetUp...")        

    def check_libraries(self):
        try:
            import psutil
            logging.info(f"Loaded python libraries  successfully")
        except:
            logging.error(f"Failed to load. Installing python libraries...")
            try:
                import pip
                pip.main(['install', 'psutil'])
                import psutil
                logging.warning("Loaded modules after install.")
            except Exception as e:
                logging.error(f"Failed to install and load psutil: {e}")