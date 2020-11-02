import time
import cv2
import glob
try :
    from text_detect import load_detector, extract_text_box, resize_img
    from text_recognize import load_recognizer, extract_text
    from detection.imgproc import loadImage
    from opt import get_config
    from text_identification import load_identifier, extract_information
except ImportError:
    from src.text_detect import load_detector, extract_text_box, resize_img
    from src.text_recognize import load_recognizer, extract_text
    from src.detection.imgproc import loadImage
    from src.opt import get_config
    from src.text_identification import load_identifier, extract_information

def main(args, folder_path):
    net, refine_net = load_detector()
    model, converter = load_recognizer()
    # identifier = load_identifier()
    for image_path in glob.glob(folder_path+'/*'):
        image = loadImage(image_path)
        # image = resize_img(image,640)
        image = cv2.resize(image,(480,960))
        # t_start = time.time()
        bboxes, polys, score_text = extract_text_box(net, image, args.text_threshold,
                                                    args.link_threshold, args.low_text,
                                                    args.cuda, args.poly, refine_net)
        boxes_and_transcripts_data = extract_text(model, converter, image, polys, image_path)
        # res = extract_information(image, boxes_and_transcripts_data, identifier, image_path.split('/')[-1])

if __name__ == '__main__':
    args = get_config()
    folder_path = "/home/son/Desktop/datn20201/resource/img"
    # image_path = '/home/son/Desktop/datn20201/resource/img/receipt_1012.jpg'
    main(args,folder_path)
