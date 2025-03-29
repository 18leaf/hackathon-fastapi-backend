import qrcode
import pymongo
import argparse
import io
client = pymongo.MongoClient(
    "mongodb+srv://admin:dbUserPassword@hackathonspring25.lwmjj4g.mongodb.net/?retryWrites=true&w=majority&appName=hackathonspring25")

db = client["HACKATHONDB"]
collection = db["qr_codes"]


def generate_code(event_id):

    qr = qrcode.QRCode(
        version=3,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )

    qr.add_data(event_id)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    img_byte_array = io.BytesIO()
    img.save(img_byte_array)
    img_byte_array.seek(0)
    qr_data = {
        "event_id": event_id,
        "qr_code_image": img_byte_array.getvalue(),  # Store the binary data of the image
    }

    # Insert the data into the MongoDB collection
    collection.insert_one(qr_data)
    print(f"QR code data saved to MongoDB for event_id: {event_id}")


event_id = "67e7056c3e988a1f7879dc79"

string_to_encoe = "urlofwebstie.com/events" + event_id


generate_code(string_to_encoe)
