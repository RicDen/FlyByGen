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
    """
    Class for generating masks based on image types and configurations.
    """
    def __init__(self):
        """
        Initializes the MaskGenerator class.
        """
        logging.info(f"Starting Mask Gen")
        
        # Set the input directory for the mask generation
        self.input_directory = paths["dataset_cache"]
        
        # Create the input directory if it doesn't exist
        # if not os.path.exists(self.input_directory):
        #     os.mkdir(self.input_directory)
        
        # Load the mask configuration from the paths.json file
        with open(paths["mask_config"]) as f:
            self.mask_config = json.load(f)
        
        # Load the render parameters from the render_configs.json file
        with open(paths['render_configs']) as json_file:
            render_params = json.load(json_file)
        
        # Set the image shape based on the render parameters
        self.image_shape = (render_params["output_format"]["resolution_x"], render_params["output_format"]["resolution_y"])

        # Define input and output directories based on the pipeline version and number of generation
        self.input_dir = f"{paths['dataset_cache']}{paths['pipeline_version']+paths['number_of_generation']}"
        self.output_dir = f"{paths['dataset_cache']}{paths['mask_out']}{paths['pipeline_version']+paths['number_of_generation']}"
        
        logging.info(f"Input directory: {self.input_dir}")
        logging.info(f"Output directory: {self.output_dir}")
        
        # Process all image types in the input directory
        self.process_all_image_types(self.input_dir)


    def get_mask_image_paths(self, input_dir, image_type):
        """
        Get the paths of mask images based on the input directory and image type.

        Args:
            input_dir (str): The input directory.
            image_type (str): The image type.

        Returns:
            list: A list of mask image paths.
        """
        mask_image_paths = []
        
        if "all" in image_type:
            # If the image type is "all", get all the images in the input directory
            base_dir = os.path.join(input_dir, image_type)
            all_images = [f for f in os.listdir(base_dir) if f.endswith(".png")]
            mask_image_paths.extend([os.path.join(base_dir, image) for image in all_images])
            
            if "noise" in image_type:
                # If the image type contains "noise", get the noise types from the image type
                noise_types = image_type.split("_")[2:]
                for noise_type in noise_types:
                    # For each noise type, get the images in the corresponding noise directory
                    mask_image_paths.extend([os.path.join(input_dir, f"noise_{noise_type}", image) for image in all_images])
            
            object_dirs = ["jets", "nucleus"]
            for object_dir in object_dirs:
                # BUG: Quickfixed with if exists
                path_object_type = os.path.join(input_dir, object_dir)
                if (os.path.exists(path_object_type)):
                # For each object directory, get the images in that directory
                    object_images = [f for f in os.listdir(os.path.join(input_dir, object_dir)) if f.endswith(".png")]
                    mask_image_paths.extend([os.path.join(input_dir, object_dir, image) for image in object_images])
                    logging.info("Adding object label paths")
                else:
                    logging.warning("Specified labels do not exist. Check the MaskGenerator for existing objects")
        return mask_image_paths

    def create_mask(self, image_path, image_type):
        """
        Create a mask based on the image path and image type.

        Args:
            image_path (str): The path of the image.
            image_type (str): The image type.

        Returns:
            numpy.ndarray: The created mask.
        """
        # Read the image from the given path in grayscale
        image = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
        
        # Create a mask by setting all non-zero pixels in the image to the given image_type value
        # BUG: Quickfix for background dust from plasma, needs to be fixed in the render
        mask = np.where((image > 1), image_type, 0)
        
        
        return mask

    def get_mask_value_from_path(self, image_path):
        """
        Get the mask value and name from the image path.

        Args:
            image_path (str): The path of the image.

        Returns:
            tuple: A tuple containing the mask value and name.
        """
        object_name = None
        objects = self.mask_config.get("objects", {})
        
        # Iterate through each object type in the mask configuration
        for object_type in objects:
            if object_type in image_path:
                # If the object type is found in the image path, set the object_name variable
                object_name = object_type
                break
        
        if object_name is None:
            return None
        
        # Return the mask value and name corresponding to the object_name
        return objects[object_name], object_name

    def process_all_image_types(self, input_dir):
        """
        Process all image types in the input directory.

        Args:
            input_dir (str): The input directory.
        """
        input_folders = {}
        for combo_folders in os.listdir(input_dir):
            # logging.info(f"Combo folders: {combo_folders}")
            if os.path.isdir(os.path.join(input_dir, combo_folders)):
                folder_paths = os.path.join(input_dir, combo_folders)
                temp_output_path = os.path.join(self.output_dir, combo_folders)
            input_folders[combo_folders] = [folder_paths, temp_output_path]
            # logging.info(f"Combo folders: {combo_folders}")
        logging.info(f"All folders paths: {input_folders}")
        for input_dir_path in input_folders:
        
            # # Create the output directory if it doesn't exist
            # if not os.path.exists(self.output_dir):
            #     os.makedirs(self.output_dir)
            path_input_combo = input_folders[input_dir_path][0]
            path_output_combo = input_folders[input_dir_path][1]
            if not os.path.exists(path_output_combo):
                os.makedirs(path_output_combo)
            logging.info(f"Created output directory: {path_output_combo}")
            all_folders = [folder for folder in os.listdir(path_input_combo) if folder.startswith("all")]
            logging.info(f"Folders: {all_folders}")
            # Iterate through each image type folder
            for image_type_name in all_folders:
                logging.info(f"Image type name: {image_type_name}")
                # Create an empty mask
                mask = np.zeros(self.image_shape, dtype=np.uint8)

                # Get the paths of mask images for the current image type
                mask_image_paths = self.get_mask_image_paths(path_input_combo, image_type_name)
                logging.info(f"Processing {image_type_name}:")
                logging.info(f"Mask image paths: {mask_image_paths}")
                logging.info("\n")

                # Iterate through each mask image path
                combined_masks = {}
                for image_path in mask_image_paths:
                    image_filename = os.path.basename(image_path)
                    if not "all" in image_path:
                        logging.info(f"Getting mask for: {image_path}")

                        # Get the mask value and name from the image path
                        mask_value, mask_name = self.get_mask_value_from_path(image_path)
                        logging.info(f"Got mask {mask_name} with value {mask_value}")

                        # Create a single mask based on the image path and mask value
                        single_mask = self.create_mask(image_path, mask_value)

                        # Define the path to save the single mask
                        # Get the image file name from the image path
                        logging.info(f"Image file name: {image_filename}")
                        path_mask = os.path.join(path_output_combo, mask_name)
                        if not os.path.exists(path_mask):
                            os.makedirs(path_mask)
                        single_mask_path = os.path.join(path_mask,image_filename)
                        logging.info(f"Saving to: {single_mask_path}")

                        # Save the single mask as an image
                        cv2.imwrite(single_mask_path, single_mask)
                        # Add the single mask to the overall mask
                        if image_filename not in combined_masks:
                            combined_masks[image_filename] = single_mask
                        else:
                            combined_masks[image_filename] += single_mask

                
                for key, mask in combined_masks.items():
                    # Define the path to save the combined mask
                            
                    if not os.path.exists(os.path.join(path_output_combo, "combined")):
                        os.makedirs(os.path.join(path_output_combo, "combined"))
                    full_mask_path = os.path.join(path_output_combo, "combined", key)
                    logging.info(full_mask_path)
                    # Save the full mask as an image
                    cv2.imwrite(full_mask_path, mask)

        # logging.info(f"{image_filenames[0]}")
        # self.apply_noise_to_dataset(image_filenames[0], noise_config)
        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     executor.map(lambda filename: self.apply_noise_to_dataset(filename, noise_config), image_filenames)
