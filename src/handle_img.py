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
    from utils.visualize import visual_confusion_matrix
except ImportError:
    from src.text_detect import load_detector, extract_text_box, resize_img
    from src.text_recognize import load_recognizer, extract_text
    from src.detection.imgproc import loadImage
    from src.opt import get_config
    from src.text_identification import load_identifier, extract_information
    from src.utils.visualize import visual_confusion_matrix

def main(args, folder_path):
    net, refine_net = load_detector()
    model, converter = load_recognizer()
    identifier = load_identifier()

    y_pred = []
    y_true = []
    for image_path in glob.glob(folder_path+'/*'):
        # label = pd.read_csv(image_path.split('.')[0].replace('img','labels')+'.tsv',sep='\n',header=None)[0].to_list()
        image = loadImage(image_path)
        image = cv2.resize(image,(480,960))
        bboxes, polys, score_text = extract_text_box(net, image, args.text_threshold,
                                                    args.link_threshold, args.low_text,
                                                    args.cuda, args.poly, refine_net)
        boxes_and_transcripts_data = extract_text(model, converter, image, polys, image_path)
        res = extract_information(image, boxes_and_transcripts_data, identifier, image_path.split('/')[-1])
    #     y_pred += res
    #     y_true += label
    # visual_confusion_matrix(y_true,y_pred)
    
if __name__ == '__main__':
    args = get_config()
    folder_path = "/home/son/Desktop/datn20201/resource/img"
    image_path = '/home/son/Desktop/datn20201/resource/img/1086-receipt.jpg'
    main(args,folder_path)
