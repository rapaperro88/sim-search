import keras
from PIL import Image
import image_process
import numpy as np
from pathlib import Path
import pandas as pd
from urllib import request
import mimetypes
import validators





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
    # query_img = image_process.pretreat_for_resnet18(full_path, (64,64))
    query_img = image_process.pretreat_for_resnet18_2(full_path, (64,64))

    # Get feature vector as image
    query_vec = image_process.get_resnet18_vec(query_img, out_size=23, out_type="3channels")

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
