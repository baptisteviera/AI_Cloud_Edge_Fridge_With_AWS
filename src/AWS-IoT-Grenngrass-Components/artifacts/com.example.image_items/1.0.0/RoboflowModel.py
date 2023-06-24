# %%
# https://docs.roboflow.com/

# %%
# Dependencies

# %%
# pip install roboflow

#
# from matplotlib.pyplot import imshow
from roboflow import Roboflow
import json


# %%
#define utility function

'''
def imShow(path):
  import cv2
  import matplotlib.pyplot as plt
  # %matplotlib inline

  image = cv2.imread(path)
  height, width = image.shape[:2]
  resized_image = cv2.resize(image,(3*width, 3*height), interpolation = cv2.INTER_CUBIC)

  fig = plt.gcf()
  fig.set_size_inches(18, 10)
  plt.axis("off")
  #plt.rcParams['figure.figsize'] = [10, 5]
  plt.imshow(cv2.cvtColor(resized_image, cv2.COLOR_BGR2RGB))
  plt.show()
'''
# %%
# Function

# %%
# intialisation
rf = Roboflow(api_key="EdmocxaG5cmWfuuI3QXg")
project = rf.workspace().project("fridgesmart")
model = project.version(1).model

# %%
# model

# %%
def prediction_type (types, img_path="/home/pi/components/artifacts/com.example.image/1.0.0/data_fridge_content/Test_Image_Fridge2.jpg"):
    
    if types == "json":
        # infer on a local image
        predictions_json = model.predict(img_path, confidence=40, overlap=30).json()
        print(predictions_json)
        
        # infer on an image hosted elsewhere
        # print(model.predict("URL_OF_YOUR_IMAGE", hosted=True, confidence=40, overlap=30).json())
        
    elif types == "dict":
        # infer on a local image
        predictions = model.predict(img_path, confidence=40, overlap=30)
        print(predictions)
        
    elif types == "viz":
        # visualize your prediction
        predictions_visualization = model.predict(img_path, confidence=40, overlap=30).save("prediction.jpg")
        # imShow("prediction.jpg")

# %%
def items_type_in_fridge_list(img_path="/home/pi/components/artifacts/com.example.image/1.0.0/data_fridge_content/Test_Image_Fridge2.jpg"):
    items_type_in_fridge = []
    predictions = model.predict(img_path, confidence=40, overlap=30)
    for prediction in predictions:
        items_type_in_fridge.append(prediction["class"])
    return items_type_in_fridge

# %%
def items_type_in_fridge_str(img_path="/home/pi/components/artifacts/com.example.image/1.0.0/data_fridge_content/Test_Image_Fridge2.jpg", sep=", "):
    return sep.join(items_type_in_fridge_list(img_path))

# %%
# items_type_in_fridge_str()

# %%
def count_object_occurances(target_class, img_file="/home/pi/components/artifacts/com.example.image_items/1.0.0/data_fridge_content/Test_Image_Fridge2.jpg"):
  """
    Helper method to count the number of objects in an image for a given class
    :param predictions: predictions returned from calling the predict method
    :param target_class: str, target class for object count
    :return: dictionary with target class and total count of occurrences in image
  """
  predictions = model.predict(img_file)
  object_counts = {}
  for prediction in predictions:
        
    if prediction['class'] in target_class and not prediction['class'] in object_counts:
        object_counts[prediction['class']] = 0

    if prediction['class'] in target_class:
      object_counts[prediction['class']] += 1
    

  object_counts = json.dumps(object_counts)

  return object_counts
  # print(object_counts)
  

# %%
def count_object_occurances_from_folder(raw_data_location,raw_data_extension):
    
    """
    :param raw_data_location : "INSERT_PATH_TO_IMG_DIRECTORY"
    :param raw_data_extension : ".jpg" # e.g jpg, jpeg, png
    
    """

    globbed_files = glob.glob(raw_data_location + '/*' + raw_data_extension)
    ## replace target_class with name of target_class
    ## example, target class is 'face': count_object_occurances(predictions, 'face')
    for img_file in globbed_files:
        class_counts = count_object_occurances(img_file, target_class)
        print(predictions, class_counts)
        print('\n')

# %%
all_targets = ["apple", "banana", "beef", 
               "blueberries", "bread", "butter", "carrot", "cheese", "chicken", "chicken_breast", 
               "chocolate", "corn", "eggs", "flour", "goat_cheese", "green_beans", "ground_beef", "ham",
               "heavy_cream", "lime", "milk", "mushrooms", "onion", "potato", "shrimp", "spinach", 
               "strawberries", "sugar", "sweet_potato", "tomato"]

# %%
# test = count_object_occurances(all_targets)
# print(type(test))  # <class 'str'>
# %%
# count_object_occurances("milk")

# %%



