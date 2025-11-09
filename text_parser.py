from google.cloud import vision
import io

client = vision.ImageAnnotatorClient.from_service_account_json("key.json")

image_path = "test.png"

with io.open(image_path, 'rb') as image_path:
    content = image_path.read()

image_context = vision.ImageContext(
    language_hints=["pl"]
)

image = vision.Image(content=content)
#
# response = client.text_detection(image = image)
# labels = response.text_annotations
# print(labels[0].description)
# print(labels)


response = client.document_text_detection(
    image=image,
    image_context=image_context
)
print(response.text_annotations[0].description)
