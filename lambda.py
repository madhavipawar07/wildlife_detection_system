import json
import boto3
import uuid
import base64
from decimal import Decimal
from datetime import datetime

# AWS Clients
s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")

# Resources
BUCKET = "wild-life"
TABLE = dynamodb.Table("wildlife")


# -----------------------------
# Decimal Encoder
# -----------------------------
class DecimalEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


# -----------------------------
# CORS
# -----------------------------
def response(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "GET,POST,OPTIONS"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }


# -----------------------------
# Upload API
# -----------------------------
def upload_image(event):

    body = json.loads(event["body"])

    image = body["image"]

    if "," in image:
        image = image.split(",")[1]

    image_bytes = base64.b64decode(image)

    animal_id = str(uuid.uuid4())

    image_name = animal_id + ".jpg"

    print("====================================")
    print("Wildlife Detection Started")
    print("Animal ID :", animal_id)
    print("Image :", image_name)

    # Upload Image
    s3.put_object(
        Bucket=BUCKET,
        Key=image_name,
        Body=image_bytes,
        ContentType="image/jpeg"
    )

    print("Image Uploaded To S3")

    # Detect Labels
    detect = rekognition.detect_labels(
        Image={
            "S3Object": {
                "Bucket": BUCKET,
                "Name": image_name
            }
        },
        MaxLabels=30,
        MinConfidence=70
    )

    print("Rekognition Completed")

    animals = [
        "Dog",
        "Cat",
        "Lion",
        "Tiger",
        "Elephant",
        "Horse",
        "Cow",
        "Buffalo",
        "Bear",
        "Monkey",
        "Bird",
        "Deer",
        "Wolf",
        "Fox",
        "Rabbit",
        "Goat",
        "Sheep",
        "Camel",
        "Leopard",
        "Cheetah",
        "Zebra",
        "Giraffe",
        "Kangaroo",
        "Panda",
        "Koala",
        "Crocodile",
        "Snake",
        "Turtle",
        "Fish",
        "Shark"
    ]

    print("------------ LABELS ------------")

    best_animal = None

    for label in detect["Labels"]:

        if label["Name"] in animals:

            count = len(label.get("Instances", []))

            if count == 0:
                count = 1

            confidence = round(label["Confidence"], 2)

            print(f"{label['Name']} | Count={count} | Confidence={confidence}")

            if best_animal is None or confidence > float(best_animal["Confidence"]):

                best_animal = {
                    "Animal": label["Name"],
                    "Count": count,
                    "Confidence": Decimal(str(confidence))
                }

    detected = []

    if best_animal:

        detected.append(best_animal)

        print("Best Animal :", best_animal["Animal"])

    else:

        print("No Animal Found")

        detected.append({
            "Animal": "Unknown",
            "Count": 0,
            "Confidence": Decimal("0")
        })

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    TABLE.put_item(
        Item={
            "animalid": animal_id,
            "ImageName": image_name,
            "Timestamp": timestamp,
            "Animals": detected
        }
    )

    print("Stored In DynamoDB")
    print("====================================")

    return response(
        200,
        {
            "status": "success",
            "animalid": animal_id,
            "image": image_name,
            "animals": detected
        }
    )


# -----------------------------
# Count API
# -----------------------------
def get_count():

    items = TABLE.scan()["Items"]

    total_images = len(items)

    total_animals = 0

    for item in items:

        for animal in item["Animals"]:

            total_animals += animal["Count"]

    return response(
        200,
        {
            "TotalImages": total_images,
            "TotalAnimals": total_animals
        }
    )


# -----------------------------
# Lambda Handler
# -----------------------------
def lambda_handler(event, context):

    print(json.dumps(event))

    method = event.get("requestContext", {}).get("http", {}).get("method")

    path = event.get("rawPath", "")

    # Lambda Test Event
    if method is None:

        return response(
            200,
            {
                "message": "Lambda Running Successfully"
            }
        )

    if method == "POST" and path == "/upload":

        return upload_image(event)

    elif method == "GET" and path == "/count":

        return get_count()

    else:

        return response(
            404,
            {
                "message": "Invalid Route"
            }
        )