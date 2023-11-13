import logging
import os
import sys
import concurrent.futures
import json
import logging
import cv2
from PIL import Image
import numpy as np

with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])


class MaskGenerator:
    def __init__(self):
        logging.info(f"Starting Mask Gen")
        self.input_directory = paths["dataset_cache"]
        if not os.path.exists(self.input_directory):
            os.mkdir(self.input_directory)
        with open(paths["mask_config"]) as f:
            self.mask_config = json.load(f)
        with open(paths['render_configs']) as json_file:
            render_params = json.load(json_file)
        self.image_shape = (render_params["output_format"]["resolution_x"], render_params["output_format"]["resolution_y"])

        # Define input and output directories
        input_dir = f"{paths['dataset_cache']}{paths['dataset_scene']}"
        self.output_dir = f"{paths['dataset_cache']}{paths['mask_out']}"

        
        self.process_all_image_types(input_dir)


    def get_mask_image_paths(self, input_dir, image_type):
        mask_image_paths = []
        
        if "all" in image_type:
            base_dir = os.path.join(input_dir, image_type)
            all_images = [f for f in os.listdir(base_dir) if f.endswith(".png")]
            mask_image_paths.extend([os.path.join(base_dir, image) for image in all_images])
            
            if "noise" in image_type:
                noise_types = image_type.split("_")[2:]
                for noise_type in noise_types:
                    # FEATUE: filter only for noises specified in mask_config
                    mask_image_paths.extend([os.path.join(input_dir, f"noise_{noise_type}", image) for image in all_images])
            
            object_dirs = ["jets", "nucleus"]
            for object_dir in object_dirs:
                object_images = [f for f in os.listdir(os.path.join(input_dir, object_dir)) if f.endswith(".png")]
                mask_image_paths.extend([os.path.join(input_dir, object_dir, image) for image in object_images])
        #TODO return image type with each path
        return mask_image_paths

    def create_mask(self, image_path, image_type):
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        mask = np.where((image != 0), image_type, 0)
        return mask

    def get_mask_value_from_path(self, image_path):
        object_name = None
        objects = self.mask_config.get("objects", {})
        
        for object_type in objects:
            if object_type in image_path:
                # logging.info(f"Object type: {object_type} found in {image_path}")
                object_name = object_type
                break
        
        if object_name is None:
            return None
        
        return objects[object_name], object_name


    def process_all_image_types(self, input_dir):
        all_folders = [folder for folder in os.listdir(input_dir) if folder.startswith("all")]
        logging.info(f"Folders: {all_folders}")
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        for image_type_name in all_folders:
            mask = np.zeros(self.image_shape, dtype= np.uint8)
            mask_image_paths = self.get_mask_image_paths(input_dir, image_type_name)
            logging.info(f"Processing {image_type_name}:")
            logging.info("Mask image paths:", mask_image_paths)
            logging.info("\n")
            # TODO mask type should be read from json or so
            for image_path in mask_image_paths:
                if not "all" in image_path:
                    logging.info(f"Getting mask for: {image_path}")
                    mask_value, mask_name = self.get_mask_value_from_path(image_path)
                    logging.info(f"Got mask {mask_name} with value {mask_value}")
                    single_mask = self.create_mask(image_path, mask_value)
                    single_mask_path = os.path.join(self.output_dir, f"frame_mask_{image_type_name}_{mask_name}.png")
                    logging.info(f"Saving to: {single_mask_path}")
                    cv2.imwrite(single_mask_path, single_mask)
                    mask = mask + single_mask
            full_mask_path = os.path.join(self.output_dir, f"frame_mask_{image_type_name}_all.png")
            cv2.imwrite(full_mask_path, mask)
    
        # logging.info(f"{image_filenames[0]}")
        # self.apply_noise_to_dataset(image_filenames[0], noise_config)
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     executor.map(lambda filename: self.apply_noise_to_dataset(filename, noise_config), image_filenames)
