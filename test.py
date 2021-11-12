import matplotlib.pyplot as plt
import keras_ocr
import sys 

def ocr(img):
    pipeline = keras_ocr.pipeline.Pipeline()
    image = keras_ocr.tools.read(img)
    prediction_groups = pipeline.recognize(image)
    return(prediction_groups)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        file_name = sys.argv[1]
    else :
        print('no file specified')
    print(ocr(file_name))