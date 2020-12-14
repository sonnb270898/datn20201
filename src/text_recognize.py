import string

import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

import pandas as pd
import numpy as np
import csv

import re
try:
    from recognition.utils import CTCLabelConverter, AttnLabelConverter
    from recognition.dataset import RawDataset, AlignCollate, Image2TextDataset
    from recognition.model import Model
    from opt import get_config
    from detection.imgproc import sorting_bounding_box
except ImportError:
    from src.recognition.utils import CTCLabelConverter, AttnLabelConverter
    from src.recognition.dataset import RawDataset, AlignCollate, Image2TextDataset
    from src.recognition.model import Model
    from src.opt import get_config
    from src.detection.imgproc import sorting_bounding_box

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

###load_config
args = get_config()

def load_recognizer():
    """ model configuration """
    if args.sensitive:
        args.character = string.printable[:-6]

    if 'CTC' in args.Prediction:
        converter = CTCLabelConverter(args.character)
    else:
        converter = AttnLabelConverter(args.character)
    args.num_class = len(converter.character)

    if args.rgb:
        args.input_channel = 3
    model = Model(args)
    print('model input parameters', args.imgH, args.imgW, args.num_fiducial, args.input_channel, args.output_channel,
          args.hidden_size, args.num_class, args.batch_max_length, args.Transformation, args.FeatureExtraction,
          args.SequenceModeling, args.Prediction)
    model = torch.nn.DataParallel(model).to(device)

    # load model
    print('loading pretrained model from %s' % args.saved_model)
    model.load_state_dict(torch.load(args.saved_model, map_location=device))
    return model, converter

def extract_text(model,converter,image,poly,image_path=''):
    h, w, _= image.shape
    boxes_sorted_list, num_rows_dict = sorting_bounding_box(poly, w, h)
    text_results = []
    # prepare data
    AlignCollate_demo = AlignCollate(imgH=args.imgH, imgW=args.imgW, keep_ratio_with_pad=args.PAD)
    # demo_data = RawDataset(root=args.image_folder, opt=args)  # use RawDataset
    demo_data = Image2TextDataset(image,boxes_sorted_list,args)

    demo_loader = torch.utils.data.DataLoader(
        demo_data, batch_size=args.batch_size,
        shuffle=False,
        num_workers=int(args.workers),
        collate_fn=AlignCollate_demo, pin_memory=True)

    # predict
    model.eval()
    with torch.no_grad():
        for image_tensors, labels in demo_loader:
            batch_size = image_tensors.size(0)
            image = image_tensors.to(device)
            # For max length prediction
            length_for_pred = torch.IntTensor([args.batch_max_length] * batch_size).to(device)
            text_for_pred = torch.LongTensor(batch_size, args.batch_max_length + 1).fill_(0).to(device)
            if 'CTC' in args.Prediction:
                preds = model(image, text_for_pred)

                # Select max probabilty (greedy decoding) then decode index to character
                preds_size = torch.IntTensor([preds.size(1)] * batch_size)
                _, preds_index = preds.max(2)
                # preds_index = preds_index.view(-1)
                preds_str = converter.decode(preds_index, preds_size)

            else:
                preds = model(image, text_for_pred, is_train=False)

                # select max probabilty (greedy decoding) then decode index to character
                _, preds_index = preds.max(2)
                preds_str = converter.decode(preds_index, length_for_pred)

            dashed_line = '-' * 80
            # head = f'{"image_path":25s}\t{"predicted_labels":25s}\tconfidence score'
            # print(f'{dashed_line}\n{head}\n{dashed_line}')
            preds_prob = F.softmax(preds, dim=2)
            preds_max_prob, _ = preds_prob.max(dim=2)
            for pred, pred_max_prob in zip(preds_str, preds_max_prob):
                if 'Attn' in args.Prediction:
                    pred_EOS = pred.find('[s]')
                    pred = pred[:pred_EOS]  # prune after "end of sentence" token ([s])
                    pred_max_prob = pred_max_prob[:pred_EOS]
                text_results.append(pred)
                # calculate confidence score (= multiply of pred_max_prob)
                confidence_score = pred_max_prob.cumprod(dim=0)[-1]
                # print(f'{pred:25s}\t{confidence_score:0.4f}')

        res = ""
        tmp = 0
        img2csv = []
        for key, value in num_rows_dict.items():
            for i in value:
                # res = res + (" ".join(text_results[tmp:tmp+i[0]])) + ' '
                flatten_arr = np.array(i[1]).flatten()
                # point_2_string = list(map(str, flatten_arr))
                # text_box = re.sub(r"[\"\']",''," ".join(text_results[tmp:tmp+i[0]]).replace(',','\,'))
                text_box = " ".join(text_results[tmp:tmp+i[0]]).replace(',','\,')
                img2csv.append([1, flatten_arr, text_box, 'other'])
                # img2csv.append([1,*(flatten_arr.tolist())," ".join(text_results[tmp:tmp+i[0]]),'other'])
                tmp += i[0]
            # res += '\n'
        #write to csv:
        # df = pd.DataFrame(img2csv)
        # df.to_csv('/home/son/Desktop/datn20201/resource/box/'+image_path.split('/')[-1][:-3]+'tsv', index=False, header=False,
        #           quotechar='',escapechar='\\',quoting=csv.QUOTE_NONE)
    return img2csv

# if __name__ == '__main__':
#       # same with ASTER setting (use 94 char).
#
#     cudnn.benchmark = True
#     cudnn.deterministic = True
#     args.num_gpu = torch.cuda.device_count()
#
#     model, converter = load_recognizer()
#     extract_text(model, converter)
