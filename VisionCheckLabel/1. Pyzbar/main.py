from pyzbar.pyzbar import decode, Decoded
from PIL import Image
import cv2
import numpy as np

flThresh = 150
maxVal = 250

image_path = "image/081734_label.png"
image = cv2.imread(image_path)

gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

blurred = cv2.GaussianBlur(gray, (3,3), 0)

thresh = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                               cv2.THRESH_BINARY, 11, 2)


decode_objects: list[Decoded] = decode(thresh)

for obj in decode_objects:
    print(f"Type: {obj.type}, Data: {obj.data.decode('utf-8')}")

cv2.imshow("Process Image", thresh)
cv2.waitKey(0)
cv2.destroyAllWindows()

# barcodeOriginal: list[Decoded] = decode(Image.open(image_path))
# barcodeProcess: list[Decoded] = decode(thresh)

# all_barcodes = barcodeOriginal + barcodeProcess
# unique_data = set()

# print("Detected Barcode: ")

# for barcode in all_barcodes:
#     data = barcode.data.decode("utf-8")
#     if data is not unique_data:
#         unique_data.add(data)
#         print(f"Type: {barcode.type}, Data: {data}")

# if not all_barcodes:
#     print("No barcode detect")
