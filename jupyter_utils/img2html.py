import argparse
import base64
import requests

def img_to_base64(source):
    """
    Convert an image from a URL or local file path to base64-encoded format.

    This function accepts either a URL or a local file path of an image.
    It fetches the image content and encodes it in base64 format.

    Parameters:
    source (str): The URL or local file path of the image.

    Returns:
    str: The base64-encoded image content, or None if conversion fails.
    """
    try:
        if source.startswith("http://") or source.startswith("https://"):
            response =  requests.get(source)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type")
                if content_type and "image" in content_type:
                    encoded_bytes = base64.b64encode(response.content)
                    encoded_string = encoded_bytes.decode("utf-8")
                    return encoded_string
            else:
                return None
        else:
            with open(source, "rb") as image_file:
                encoded_bytes = base64.b64encode(image_file.read())
                encoded_string = encoded_bytes.decode("utf-8")
                return encoded_string
    except (requests.RequestException, FileNotFoundError):
        return None

def img2html_base64(source):
    """
    Convert an image to a base64-encoded HTML img tag.

    This function converts an image from a URL or local file path into a
    base64-encoded HTML img tag with the image as the source.

    Parameters:
    source (str): The URL or local file path of the image.

    Returns:
    str: The HTML img tag containing the base64-encoded image, or an error message.
    """
    encoded_image = img_to_base64(source)
    extention2html_tag={"png":"png", "jpg":"jpeg", "jpeg":"jpeg", "gif":"gif", "svg":"svg+xml"}
    if encoded_image:
        #recover the extention of the image
        extention = source.split(".")[-1]
        #convert the extention to the html tag
        formatter=extention2html_tag[extention]
        img_tag = f'<img src="data:image/{formatter};base64,{encoded_image}" alt="Image">'
        return img_tag
    else:
        return "Error: Unable to fetch or convert the image."

def video_to_base64(source):
    """
    Convert an video from a URL or local file path to base64-encoded format.

    This function accepts either a URL or a local file path of an video.
    It fetches the video content and encodes it in base64 format.

    Parameters:
    source (str): The URL or local file path of the video.

    Returns:
    str: The base64-encoded video content, or None if conversion fails.
    """
    try:
        if source.startswith("http://") or source.startswith("https://"):
            response = requests.get(source)
            if response.status_code == 200:
                content_type = response.headers.get("Content-Type")
                if content_type and "video" in content_type:
                    encoded_bytes = base64.b64encode(response.content)
                    encoded_string = encoded_bytes.decode("utf-8")
                    return encoded_string
            else:
                return None
        else:
            with open(source, "rb") as video_file:
                encoded_bytes = base64.b64encode(video_file.read())
                encoded_string = encoded_bytes.decode("utf-8")
                return encoded_string
    except (requests.RequestException, FileNotFoundError):
        return None

def video2html_base64(source): 
    """
    Convert an video to a base64-encoded HTML video tag.

    This function converts an video from a URL or local file path into a
    base64-encoded HTML video tag with the video as the source.

    Parameters:
    source (str): The URL or local file path of the video.

    Returns:
    str: The HTML video tag containing the base64-encoded video, or an error message.
    """
    encoded_video = video_to_base64(source)
    if encoded_video:
        video_tag = f'<video controls="controls" src="data:video/{source.split(".")[-1]};base64,{encoded_video}"></video>'
        return video_tag
    else:
        return "Error: Unable to fetch or convert the video."


def img2html_base64_parse():
    """
    Parse command-line arguments and convert an image to a base64-encoded HTML img tag.

    This function reads the image file name from command-line arguments,
    converts the image to a base64-encoded HTML img tag using the img2html_base64 function,
    and prints the resulting tag to the console.

    Returns:
    None
    """
    parser = argparse.ArgumentParser(description="Convert an image file to an HTML img tag with base64-encoded data.")
    parser.add_argument("image_name", help="The name of the image file to be converted.")
    args = parser.parse_args()
    
    print(img2html_base64(args.image_name))

def media2html_base64_parse():
    """
    Parse command-line arguments and convert an media to a base64-encoded HTML media tag.

    This function reads the media file name from command-line arguments,
    converts the media to a base64-encoded HTML media tag using the media2html_base64 function,
    and prints the resulting tag to the console.

    Returns:
    None
    """
    parser = argparse.ArgumentParser(description="Convert an media file to an HTML media tag with base64-encoded data.")
    parser.add_argument("media_name", help="The name of the media file to be converted.")
    args = parser.parse_args()
    
    if args.media_name.endswith((".mp4", ".webm", ".ogg")):
        print(video2html_base64(args.media_name))
    elif args.media_name.endswith((".png", ".jpg", ".jpeg", ".gif", ".svg")) :
        print(img2html_base64(args.media_name))

    return

if __name__ == "__main__":
    media2html_base64_parse()
