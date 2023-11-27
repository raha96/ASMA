from sys import argv
from encode_file import create_all_vectors_list
from ast_gen import ast_from_file, ast_from_str
import keras
import numpy as np

def _predict(ast) -> tuple:
    original_feature_vector = create_all_vectors_list(ast)[0]
    out = {"token_count": len(original_feature_vector)}
    for model_name in ["good", "labeled", "sensitivity", "transitions", "hasfsm"]: 
        feature_vector = original_feature_vector
        model = keras.models.load_model(f"models/{model_name}.keras")
        config = model.get_config()
        expected_length = config["layers"][0]["config"]["batch_input_shape"][1]
        for _ in range(len(feature_vector), expected_length):
            feature_vector.append(0)
        x = np.array(feature_vector)
        x = x.reshape((1, expected_length))
        pred = model(x)
        out[model_name] = bool(pred[0] >= 0.5)
    return out

def predict(filename:str) -> tuple:
    ast = ast_from_file(filename)
    return _predict(ast)

def predict_str(source:str) -> tuple:
    ast = ast_from_str(source)
    return _predict(ast)

if __name__ == "__main__":
    print(predict(argv[1]))