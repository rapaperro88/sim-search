import os
from torchvision import transforms, models
import torch
from sklearn.model_selection import StratifiedShuffleSplit
from collections import defaultdict
import keras
from PIL import Image
import numpy as np
from pathlib import Path
import pandas as pd
from urllib import request
import mimetypes
import validators


class Img2VecResnet18:
    def __init__(self):
        self.device = torch.device("cpu")
        self.numberFeatures = 512
        self.modelName = "resnet-18"
        self.model, self.featureLayer = self.getFeatureLayer()
        self.model = self.model.to(self.device)
        self.model.eval()
        self.toTensor = transforms.ToTensor()

        # normalize the resized images as expected by resnet18
        # [0.485, 0.456, 0.406] --> normalized mean value of ImageNet, [0.229, 0.224, 0.225] std of ImageNet
        self.normalize = transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

    def getVec(self, img):
        image = self.normalize(self.toTensor(img)).unsqueeze(0).to(self.device)
        embedding = torch.zeros(1, self.numberFeatures, 1, 1)

        def copyData(m, i, o): embedding.copy_(o.data)

        h = self.featureLayer.register_forward_hook(copyData)
        self.model(image)
        h.remove()

        return embedding.numpy()[0, :, 0, 0]

    def getFeatureLayer(self):
        cnnModel = models.resnet18(pretrained=True)
        layer = cnnModel._modules.get('avgpool')
        self.layer_output_size = 512

        return cnnModel, layer

def resize_and_crop(img, size, crop_type='middle', resize=True):
    """
    Resize and crop an image to fit the specified size.
    args:
        img_path: path for the image to resize.
        modified_path: path to store the modified image.
        size: `(width, height)` tuple.
        crop_type: can be 'top', 'middle' or 'bottom', depending on this
            value, the image will cropped getting the 'top/left', 'midle' or
            'bottom/rigth' of the image to fit the size.
    raises:
        Exception: if can not open the file in img_path of there is problems
            to save the image.
        ValueError: if an invalid `crop_type` is provided.

    https://gist.github.com/sigilioso/2957026
    """
    if type(img) == str:  # if img is a path
        img = Image.open(img)

    if isinstance(img, Image.Image):  # If type(img) == PIL.Image.Image

        # If height is higher we resize vertically, if not we resize horizontally
        # Get current and desired ratio for the images
        img_ratio = img.size[0] / float(img.size[1])
        ratio = size[0] / float(size[1])
        # The image is scaled/cropped vertically or horizontally depending on the ratio
        if ratio > img_ratio:
            img = img.resize((size[0], size[0] * img.size[1] // img.size[0]),
                             Image.ANTIALIAS)
            # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, img.size[0], size[1])
            elif crop_type == 'middle':
                box = (0, (img.size[1] - size[1]) / 2, img.size[0], (img.size[1] + size[1]) / 2)
            elif crop_type == 'bottom':
                box = (0, img.size[1] - size[1], img.size[0], img.size[1])
            else:
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)
        elif ratio < img_ratio:
            img = img.resize((size[1] * img.size[0] // img.size[1], size[1]),
                             Image.ANTIALIAS)
            # Crop in the top, middle or bottom
            if crop_type == 'top':
                box = (0, 0, size[0], img.size[1])
            elif crop_type == 'middle':
                box = ((img.size[0] - size[0]) / 2, 0, (img.size[0] + size[0]) / 2, img.size[1])
            elif crop_type == 'bottom':
                box = (img.size[0] - size[0], 0, img.size[0], img.size[1])
            else:
                raise ValueError('ERROR: invalid value for crop_type')
            img = img.crop(box)
        elif resize:
            img = img.resize((size[0], size[1]),
                             Image.ANTIALIAS)
            # If the scale is the same, we do not need to crop
        return img

    else:
        raise ValueError("img data type not recognized")


def pretreat_for_resnet18(img_path: str, reshape_to: tuple=(64,64), grayscale:bool=True):
    """
    Returns resized image as a numpy array

    Arguments:

        * reshape_to [2-tuple]: shape of output image
    """
    if type(img_path) == str: # if path
        img = Image.open(img_path)
    elif type(img_path) == np.ndarray: # if array
        img = Image.fromarray(img_path)

    if img.size != reshape_to:  # then img needs to be resized
        img = resize_and_crop(img, reshape_to)
    new_img = np.array(img)

    if new_img.shape[-1] == 4: # i.e. ignore transparent channel
        new_img = new_img[:,:,:3]

    if new_img.shape[-1] == 2: # i.e. ignore transparent channel
        new_img = new_img[:,:,0]

    if new_img.ndim == 2:  # i.e. grayscale -> add dummy channels
        new_img = np.stack((new_img,) * 3, axis=-1)
        return np.clip(new_img, a_min=0, a_max=255).astype(np.uint8)

    if new_img.shape[-1] >= 3 and grayscale:
        new_img = np.dot(new_img[..., :3], [0.2989, 0.5870, 0.1140])
        new_img = np.stack((new_img,) * 3, axis=-1)

    return np.clip(new_img, a_min = 0, a_max = 255).astype(np.uint8)

def pretreat_for_resnet18_2(img_path: str, reshape_to: tuple=(224,224), grayscale:bool=False):
    """
    Returns resized image as a numpy array

    Arguments:

        * reshape_to [2-tuple]: shape of output image
    """

    transformationForCNNInput = transforms.Compose([transforms.Resize(reshape_to)])

    if type(img_path) == str: # if path
        img = Image.open(img_path)
    elif type(img_path) == np.ndarray: # if array
        img = Image.fromarray(img_path)

    if img.size != reshape_to:  # then img needs to be resized
        img = transformationForCNNInput(img)
    new_img = np.array(img)

    if new_img.shape[-1] == 4: # i.e. ignore transparent channel
        new_img = new_img[:,:,:3]

    if new_img.shape[-1] == 2: # i.e. ignore transparent channel
        new_img = new_img[:,:,0]

    if new_img.ndim == 2:  # i.e. grayscale -> add dummy channels
        new_img = np.stack((new_img,) * 3, axis=-1)
        return np.clip(new_img, a_min=0, a_max=255).astype(np.uint8)

    if new_img.shape[-1] >= 3 and grayscale:
        new_img = np.dot(new_img[..., :3], [0.2989, 0.5870, 0.1140])
        new_img = np.stack((new_img,) * 3, axis=-1)

    return np.clip(new_img, a_min = 0, a_max = 255).astype(np.uint8)

# if I.ndim == 2:
#     I = np.stack((a,) * 3, axis=-1)
# if I.shape[-1] == 4:
#     I = I[:, :, :3]
# I = np.clip(I, a_min=0, a_max=255).astype(np.uint8)



def get_resnet18_vec(img, out_size=23, out_type="3channels"):
    """
        Uses: class Img2VecResnet18()

        Arguments :

            * out_type [str] :

                * "3channels" : returns a vector as an image, reshaped to
                    (out_size, out_size, 3)

                * "1channel" : returns a vector as an image, reshaped to
                    (out_size, out_size, 1)

                * "vector" : returns a feature vector. Ignores out_shape.

            Note : for reshaping to desired shape, missing values are completed
                by the mean value in the form of trailing pixels.
        """
    rn_vec_size = 512
    img2vec = Img2VecResnet18()

    if img.shape[-1] == 4:
        img = img[:,:,:3]

    vec = img2vec.getVec(img)
    if out_type == "vector":
        return vec

    # min size of output below which data is lost
    min_size = int(np.ceil(np.sqrt(rn_vec_size)))

    if out_size < min_size:
        raise ValueError("out_type '3channels' and '1channel' not supported for \
        output feature image size < np.ceil(np.sqrt(rn_vec_size))")

    # complete missing data
    missing_data = int(out_size ** 2 - rn_vec_size)
    if missing_data == 0:
        pass
    else:
        vec_1_channel = np.r_[vec, [np.mean(vec)] * missing_data]

    if out_type == "1channel":
        return vec_1_channel.reshape((out_size, out_size, 1))

    if out_type == "3channels":
        vec_img = vec_1_channel.reshape((out_size, out_size))
        return np.stack((vec_img,) * 3, axis=-1)


def get_similars_dummy(query_path: str, nb: int):
    print(query_path)
    print(nb)
    path_list = ["static/img/chien_2.PNG", "static/img/chien_3.PNG"]
    return path_list

def get_similars(full_path:str=None, nb_responses:str="2"):

    model_num = 2

    nb_responses = int(nb_responses)

    if not full_path:
        similars_paths = ["static/img/chien_2.PNG", "static/img/chien_3.PNG"]
        return similars_paths

    # Load model & embeddings
    model = load_model(model_num)
    embeddings = load_embeddings(model_num)

    # Get processed query img as numpy array
    # query_img = pretreat_for_resnet18(full_path, (64,64))
    query_img = pretreat_for_resnet18_2(full_path, (64,64))

    # Get feature vector as image
    query_vec = get_resnet18_vec(query_img, out_size=23, out_type="3channels")

    # Predict image from RN18 vector (reshaped as image)
    single_vec = np.expand_dims(query_vec, axis=0)
    prediction = model.predict(single_vec)

    # Append new embeddings to old ones
    tmp_embeddings = np.concatenate([embeddings, prediction])

    # Compute relative distances matrix
    gram_matrix = np.einsum("ae,be->ab", tmp_embeddings, tmp_embeddings)

    nn = min((nb_responses + 10),len(embeddings))
    near_neighbours = np.argsort(gram_matrix.T)[:, -(nn + 1):]

    query_nns = list(reversed(near_neighbours[-1][:-1]))


    url_table_path = f"/home/afl/Documents/data/pco_1/url_{model_num}.pkl"
    urls = pd.read_pickle(url_table_path)
    print("---------------------", urls.shape, len(embeddings), len(query_nns))

    return_list = []

    for i in query_nns:
        # try:
        url = urls[i]
        if validators.url(url):
            return_list.append(url)
        if len(return_list) == nb_responses:
            break
        # except:
        #     pass



    # Sort distances matrix by shortest distances
    # near_neighbours = np.argsort(gram_matrix)[-1:,:]

    # Keep nb_responses only
    # print(">>>>>>>>>>>>> NN", near_neighbours[:100])
    # nearest_neighbours = list(near_neighbours[:, :nb_responses])[0]


    # Load images dataset ---------------------------------------------
    # TODO: replace by SQL Database query

    # data_path = "/home/afl/Documents/data/pco_1/data_4.npy"
    # with open(data_path, 'rb') as f:
    #     x = np.load(f)
    #     all_ima = np.load(f)
    #     y = np.load(f)
    #
    # answer_imgs = all_ima[nearest_neighbours, :,:,:]
    # tmp_folder = "static/tmp"
    # Path(tmp_folder).mkdir(parents=True, exist_ok=True)
    # similars_paths = []
    # for i, img_array in enumerate(answer_imgs):
    #     path = tmp_folder + f"/answer_{i}.jpg"
    #     img = Image.fromarray(img_array)
    #     img.save(path)
    #     similars_paths.append(path)

    # url_table_path = f"/home/afl/Documents/data/pco_1/url_{model_num}.pkl"
    # urls = pd.read_pickle(url_table_path)
    # print("-------------------->", len(urls))
    # answer_urls = urls.loc[return_list, "url"]



    # -------------------------------------------------------------------
    return return_list

def load_model(model_num:int):

    # Load embeddings
    folder = f"../data_retrieval/model_{model_num}"
    model = keras.models.load_model(folder)

    return model


def load_embeddings(model_num:int):
    embeddings_path = f"/home/afl/Documents/data/pco_1/embeddings_{model_num}.npy"
    with open(embeddings_path, 'rb') as f:
        embeddings = np.load(f)
    return embeddings


def get_similar_from_cifar_10():
    result_img_path = None

    # predict, concatenate, retrieve images
    # Save image
    # Return url to image

    return result_img_path
