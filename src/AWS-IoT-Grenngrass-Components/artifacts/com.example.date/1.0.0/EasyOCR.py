# %%
import easyocr
import cv2
from dateutil.parser import parse

def is_date(string, fuzzy=False):
    """
    Return whether the string can be interpreted as a date.

    :param string: str, string to check for date
    :param fuzzy: bool, ignore unknown tokens in string if True
    """
    try: 
        parse(string, fuzzy=fuzzy)
        return True

    except ValueError:
        return False

# %%
def expiry_date(liste):
    expiry_date = []
    for i in liste:
        if is_date(i) and len(i)>2:
            expiry_date.append(i)
    return expiry_date

    
def date_expiry(image_path = "/home/pi/components/artifacts/com.example.date/1.0.0/data_expiry_date/date_expriration2.png"):

    reader = easyocr.Reader(["en"],gpu=False)
    result = reader.readtext(image_path)
    # print(result)
    list_result = []

    for res in result:
        list_result.append(res[1])

    # print(list_result)
    # type(list_result[-2])

    return expiry_date(list_result)


date_expiry()



