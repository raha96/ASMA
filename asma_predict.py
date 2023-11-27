from sys import argv
from encode_file import create_all_vectors_list
from ast_gen import ast_from_file
import keras
import numpy as np

def predict(filename:str) -> dict:
    ast = ast_from_file(filename)
    out = {}
    for model_name in ["good", "labeled", "sensitivity", "transitions", "hasfsm"]: 
        featurevectors = create_all_vectors_list(ast)[0]
        model = keras.models.load_model(f"models/{model_name}.keras")
        config = model.get_config()
        expected_length = config["layers"][0]["config"]["batch_input_shape"][1]
        for _ in range(len(featurevectors), expected_length):
            featurevectors.append(0)
        x = np.array(featurevectors)
        x = x.reshape((1, expected_length))
        pred = model(x)
        out[model_name] = bool(pred[0] >= 0.5)
    return out

if __name__ == "__main__":
    print(predict(argv[1]))