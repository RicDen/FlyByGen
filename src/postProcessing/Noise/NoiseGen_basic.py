import logging
import os
import sys
import concurrent.futures
import json
import logging
import cv2
from PIL import Image
import numpy as np
import random
import itertools
with open('src/config/paths.json', 'r') as f:
    paths = json.load(f)

sys.path.append(paths['project_directory'])


class BasicNoiseGenerator:
    """
        Allows to create basic noise for a given dataset folder defined in the json file.
        Currently, Gaussian, Poisson, and Salt/Pepper noise are supported.
        This generator creates noise according to the noise.json and creates all combinations of the different noises in different images.
        This generator supports multithreading.
    """
    def __init__(self):
        logging.info(f"Starting Noise Gen")
        with open(paths['noise_config']) as json_file:
            noise_params = json.load(json_file)
        with open(paths['render_configs']) as json_file:
            render_params = json.load(json_file)
        self.dataset_folder = paths["dataset_cache"]+paths["pipeline_version"]+paths["number_of_generation"]
        self.processing_basis = paths["post_processing_basis"]
        self.processing_output = paths["noise_output"]
        self.image_shape = (render_params["output_format"]["resolution_x"], render_params["output_format"]["resolution_y"])

        self.process_dataset(noise_params)

    def create_gaussian_noise(self, mean=0.0, std=1.0):
        """
            Creates Gaussian noise according to the defined image size

            :param mean: Mean value of the gaussian distribution (default: 0.0)
            :type: float
            :param std: Standard deviation of the distribution (default: 1.0)
            :type: float
            :return: np array with image dimensions and generated noise
            :type: np.array
        """
        noise_grayscale = np.random.normal(mean, std, self.image_shape)
        noise_gaus = np.stack([noise_grayscale] * 3, axis=-1)
        noise_gaus = np.clip(noise_gaus, 0, 255).astype(np.uint8)
        return noise_gaus


    def create_poisson_noise(self, image, poisson_amount=0.05):
        """
            Creates Poisson noise based on the image and the defined image size

            :param poisson_amount: Intensity of the Poisson noise (default: 0.05)
            :type: float
            :return: np array with image dimensions and generated noise
            :type: np.array
        """
        noisy_image_r = np.random.poisson(image[:,:,0] * (1 + poisson_amount))
        noise = np.stack([noisy_image_r] * 3, axis=-1)
        noise = np.clip(noise, 0, 255).astype(np.uint8)
        return noise

    def create_salt_and_pepper_noise(self, image, amount=0.05):
        """
            Creates Salt and Pepper noise based on the image and the defined image size

            :param poisson_amount: Intensity of the Salt and Pepper noise (default: 0.05)
            :type: float
            :return: np array with image dimensions and generated noise
            :type: np.array
        """
        noise_sp = np.zeros_like(image)
        num_pixels = int(np.prod(self.image_shape) * amount)

        for _ in range(num_pixels):
            x = random.randint(0, self.image_shape[0] - 1)
            y = random.randint(0, self.image_shape[1] - 1)
            noise_sp[x, y] = random.choice([0, 255])
        noise_sp = np.clip(noise_sp, 0, 255).astype(np.uint8)
        return noise_sp

    def store_noises(self, image_filename, noise_list):
        """
            Save each created noise array as image separately

            :param image_filename: Specifies the image filename to have the correct reference to the base image
            :type: str
            :param noise_list: List of noises generated
            :type: list
        """
        for noise, noise_type in noise_list:
            noise_type_dir = os.path.join(self.dataset_folder, f"noise_{noise_type}")
            if not os.path.exists(noise_type_dir):
                os.makedirs(noise_type_dir)
            noise_path = os.path.join(noise_type_dir, image_filename)
            cv2.imwrite(noise_path, noise)
            logging.info(f"Noise saved to {noise_path}")

    def store_noisy_images(self, image_filename, noisy_image_list):
        """
            Save each create image with noise as image separately

            :param image_filename: Specifies the image filename to have the correct reference to the base image
            :type: str
            :param noise_list: List of noisy images generated
            :type: list
        """
        for noisy_image, noise_type in noisy_image_list:
            noisy_image_type_image_dir = os.path.join(self.dataset_folder, f"all_noise_{noise_type}")
            if not os.path.exists(noisy_image_type_image_dir):
                os.makedirs(noisy_image_type_image_dir)
            noisy_image_path = os.path.join(noisy_image_type_image_dir, image_filename)
            cv2.imwrite(noisy_image_path, noisy_image)
            logging.info(f"Noisy image {image_filename} saved to {noisy_image_path}")

    def mix_noises(self, image, noise_list):
        """
            Create each combination of the different available noises
            
            :param image: Passes the base image on which the noise shall be applied
            :type: np.array
            :param noise_list: List of noises generated
            :type: list
        """
        logging.info(f"Mixing noises...")
        noisy_images = []

        for r in range(1, len(noise_list) + 1):
            for combination in itertools.combinations(noise_list, r):
                noisy_image = image.copy()  # Create a copy of the original image
                logging.info(f"Combination...")
                combination_name = ""
                for noise, noise_type in combination:
                    combination_name = combination_name+f"_{noise_type}"
                    logging.info(f"Adding noise: {noise_type}")
                    noisy_image = noisy_image + noise
                    noisy_image = np.clip(noisy_image, 0, 255).astype(np.uint8)

                noisy_images.append((noisy_image, combination_name))
                logging.info(f"Combination name: {combination_name}")

        return noisy_images


# FEATURE: Allow to apply multiple different noise configs per run
    def apply_noise_to_dataset(self, image_filename, noise_config):
        """
            Applies noises according to the noise configuration to the image given via its filename

            :param image_filename: Specificies the image file name to load and save the file accordingly
            :type: str
            :param noise_config: This is a dictionary loaded from a json file containing the parameters required for the creation of noise
            :type: dict
        """
        if image_filename.endswith(".png"):
            logging.info(f"Started image {image_filename}")
            image_path = os.path.join(self.dataset_folder, self.processing_basis, image_filename)
            image = cv2.imread(image_path)
            noise_basis_image = image.copy()

            noise_list = []
            logging.info(f"Creating noises...")
            for noise_type, noise_params in noise_config.items():
                logging.info(f"...{noise_type} with {noise_params}")
                if noise_params["enabled"]:
                    if "SP" in noise_type:
                        noise_sp = self.create_salt_and_pepper_noise(noise_basis_image, amount=noise_params["amount"])
                        noise_list.append((noise_sp, "sp"))
                    elif "gaussian" in noise_type:
                        noise_gauss = self.create_gaussian_noise(mean=noise_params["mean"], std=noise_params["std"])
                        noise_list.append((noise_gauss, "gauss"))
                    elif "poisson" in noise_type:
                        noise_poisson = self.create_poisson_noise(noise_basis_image, poisson_amount=noise_params["amount"])
                        noise_list.append((noise_poisson, "poisson"))
                    else:
                        logging.error(f"Unknown noise: {noise_type}")

            self.store_noises(image_filename, noise_list)
            noisy_images = self.mix_noises(image, noise_list)
            self.store_noisy_images(image_filename, noisy_images)

    def process_dataset(self, noise_config):
        """
            Runs the process with a threa pool executor to use multhreading

            :param noise_config: This is a dictionary loaded from a json file containing the parameters required for the creation of noise
            :type: dict
        """
        image_filenames = os.listdir((self.dataset_folder + self. processing_basis))
        with concurrent.futures.ThreadPoolExecutor() as executor:
            executor.map(lambda filename: self.apply_noise_to_dataset(filename, noise_config), image_filenames)
