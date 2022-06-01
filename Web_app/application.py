from email.mime import application
import os
import boto3
from flask import Flask, render_template, request

cwd = os.getcwd()
application = Flask(__name__)

aws_access_id = ""#accesskey
aws_secret_access_key = ""#seceretaccesskey
image_bucket = "image-ramsai"
text_bucket = "text-services-ramsai"
bucket = "bucket-mlops-ramsai"

@application.route("/")
@application.route("/home")
def home():
    return render_template("home.html")

@application.route("/image")
def image():
    return render_template("image.html")

@application.route("/text")
def text():
    return render_template("text.html")

@application.route("/postimage", methods=["GET", "POST"])
def postimage():
    if request.method == "POST":
        # os.remove(f"{cwd}/images/*")
        if 'file1' not in request.files:
            return "No image uploaded !!"
        file1 = request.files['file1']
        path = os.path.join(f"{cwd}/images/", file1.filename)
        file1.save(path)
        s3 = boto3.client("s3",
                          region_name='ap-south-1',
                          aws_access_key_id=aws_access_id,
                          aws_secret_access_key=aws_secret_access_key)

        s3.upload_file(path, bucket, file1.filename)
    return render_template("home.html")


@application.route("/posttext", methods=["GET", "POST"])
def posttext():
    if request.method == "POST":
        # os.remove(f"{cwd}/texts/*")
        text = request.form["input_text"]
        with open(f"{cwd}/texts/text.txt", "w+") as f:
            f.write(text)
        s3 = boto3.client("s3",
                          region_name='ap-south-1',
                          aws_access_key_id=aws_access_id,
                          aws_secret_access_key=aws_secret_access_key)

        s3.upload_file(f"{cwd}/texts/text.txt", bucket, "text.txt")
    return render_template("home.html")

if __name__ == "__main__":
    application.run(debug=True)