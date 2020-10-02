import string

import torch
import torch.backends.cudnn as cudnn
import torch.utils.data
import torch.nn.functional as F

try:
    from .recognition.utils import CTCLabelConverter, AttnLabelConverter
    from .recognition.dataset import RawDataset, AlignCollate, Image2TextDataset
    from .recognition.model import Model
    from .opt import get_config
    from .detection.imgproc import sorting_bounding_box
except ImportError:
    from src.recognition.utils import CTCLabelConverter, AttnLabelConverter
    from src.recognition.dataset import RawDataset, AlignCollate, Image2TextDataset
    from src.recognition.model import Model
    from src.opt import get_config
    from src.detection.imgproc import sorting_bounding_box
import time
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')

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

def extract_text(model,converter,image,poly):
    num_rows = sorting_bounding_box(poly)
    text_results = []
    # prepare data
    AlignCollate_demo = AlignCollate(imgH=args.imgH, imgW=args.imgW, keep_ratio_with_pad=args.PAD)
    # demo_data = RawDataset(root=args.image_folder, opt=args)  # use RawDataset
    demo_data = Image2TextDataset(image,poly,args)

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

            log = open(f'./log_demo_result.txt', 'a')
            dashed_line = '-' * 80
            head = f'{"image_path":25s}\t{"predicted_labels":25s}\tconfidence score'            
            print(f'{dashed_line}\n{head}\n{dashed_line}')
            log.write(f'{dashed_line}\n{head}\n{dashed_line}\n')
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
                print(f'{pred:25s}\t{confidence_score:0.4f}')
                log.write(f'{pred:25s}\t{confidence_score:0.4f}\n')
            log.close()

        res = ""
        tmp = 0
        for i in num_rows:
            res += (" ".join(text_results[tmp:tmp+i]) + "\n")
            tmp += i
    return res

# if __name__ == '__main__':
#       # same with ASTER setting (use 94 char).
#
#     cudnn.benchmark = True
#     cudnn.deterministic = True
#     args.num_gpu = torch.cuda.device_count()
#
#     model, converter = load_recognizer()
#     extract_text(model, converter)
