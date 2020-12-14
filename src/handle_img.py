import time
import cv2
import glob
import pandas as pd

try :
    from text_detect import load_detector, extract_text_box, resize_img
    from text_recognize import load_recognizer, extract_text
    from detection.imgproc import loadImage
    from opt import get_config
    from text_identification import load_identifier, extract_information
    from utils.label_rules import convert_result_to_json
except ImportError:
    from src.text_detect import load_detector, extract_text_box, resize_img
    from src.text_recognize import load_recognizer, extract_text
    from src.detection.imgproc import loadImage
    from src.opt import get_config
    from src.text_identification import load_identifier, extract_information
    from src.utils.label_rules import convert_result_to_json

args = get_config()
net, refine_net = load_detector()
model, converter = load_recognizer()
identifier = load_identifier()

def extract_receipt(image_path):
    image = loadImage(image_path)
    # image = cv2.resize(image,(480,960))
    bboxes, polys, score_text = extract_text_box(net, image, args.text_threshold,
                                                args.link_threshold, args.low_text,
                                                args.cuda, args.poly, refine_net)
    boxes_and_transcripts_data = extract_text(model, converter, image, polys)
    boxes_and_transcripts_data = extract_information(image, boxes_and_transcripts_data, identifier)
    res = convert_result_to_json(boxes_and_transcripts_data)
    return res

if __name__ == '__main__':
    image_path = '/home/son/Downloads/CORD/full_receipt_en/images/1141-receipt.jpg'
    image = cv2.imread(image_path)
    extract_receipt(image)
