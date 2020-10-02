import time

try :
    from .text_detect import load_detector, extract_text_box, resize_img
    from .text_recognize import load_recognizer, extract_text
    from .detection.imgproc import *
    from .opt import get_config
except ImportError:
    from src.text_detect import load_detector, extract_text_box, resize_img
    from src.text_recognize import load_recognizer, extract_text
    from src.detection.imgproc import *
    from src.opt import get_config

def main(args,image_path):
    net, refine_net = load_detector()
    model, converter = load_recognizer()

    image = loadImage(image_path)
    image = resize_img(image,640)
    t_start = time.time()
    bboxes, polys, score_text = extract_text_box(net, image, args.text_threshold,
                                                 args.link_threshold, args.low_text,
                                                 args.cuda, args.poly, refine_net)
    text = extract_text(model, converter, image, polys)
    print(text)

if __name__ == '__main__':
    args = get_config()
    img_path = "/home/son/Desktop/text-detection/bill/bill_02.jpg"
    main(args,img_path)