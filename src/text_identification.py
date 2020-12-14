import torch
from tqdm import tqdm
from pathlib import Path
# import pandas as pd
# import csv
from torch.utils.data.dataloader import DataLoader
from allennlp.data.dataset_readers.dataset_utils.span_utils import bio_tags_to_spans

try:
    from parse_config import ConfigParser
    import identification.model.pick as pick_arch_module
    from identification.data_utils.pick_dataset import PICKDataset, TestingDataset
    from identification.data_utils.pick_dataset import BatchCollateFn
    from identification.utils.util import iob_index_to_str, text_index_to_str
    from identification.utils.class_utils import set_vocab
    from opt import get_config
    from utils.label_rules import Label_rules
except ImportError:
    from src.parse_config import ConfigParser
    import src.identification.model.pick as pick_arch_module
    from src.identification.data_utils.pick_dataset import PICKDataset, TestingDataset
    from src.identification.data_utils.pick_dataset import BatchCollateFn
    from src.identification.utils.util import iob_index_to_str, text_index_to_str
    from src.identification.utils.class_utils import set_vocab
    from src.opt import get_config
    from src.utils.label_rules import Label_rules

import cv2
import os
import numpy as np

args = get_config()
device = torch.device("cuda:0" if torch.cuda.is_available() else 'cpu')

def load_identifier():
    checkpoint = torch.load(args.checkpoint, map_location=device)
    config = checkpoint['config']
    state_dict = checkpoint['state_dict']
    monitor_best = checkpoint['monitor_best']
    print('Loading checkpoint: {} \nwith saved mEF {:.4f} ...'.format(args.checkpoint, monitor_best))
    entities_list = config['train_dataset']['args']['entities_list']
    set_vocab(entities_list)
    # prepare model for testing
    pick_model = config.init_obj('model_arch', pick_arch_module)
    pick_model = pick_model.to(device)
    pick_model.load_state_dict(state_dict)
    pick_model.eval()
    return pick_model

def extract_information(image, boxes_and_transcripts_data, pick_model, save_image=''):
    # setup dataset and data_loader instances
    test_dataset = TestingDataset(image=image,
                                  boxes_and_transcripts_data=boxes_and_transcripts_data,
                                  ignore_error=False,
                                )
    test_data_loader = DataLoader(test_dataset, batch_size=1, shuffle=False,
                                  num_workers=0, collate_fn=BatchCollateFn(training=False))

    # setup output path
    output_path = Path(args.output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    # predict and save to file
    with torch.no_grad():
        for step_idx, input_data_item in tqdm(enumerate(test_data_loader)):
            for key, input_value in input_data_item.items():
                if input_value is not None and isinstance(input_value, torch.Tensor):
                    input_data_item[key] = input_value.to(device)

            output = pick_model(**input_data_item)
            logits = output['logits']  # (B, N*T, out_dim)
            new_mask = output['new_mask']
            image_indexs = input_data_item['image_indexs']  # (B,)
            text_segments = input_data_item['text_segments']  # (B, num_boxes, T)
            mask = input_data_item['mask']
            # List[(List[int], torch.Tensor)]
            best_paths = pick_model.decoder.crf_layer.viterbi_tags(logits, mask=new_mask, logits_batch_first=True)
            predicted_tags = []
            for path, score in best_paths:
                predicted_tags.append(path)

            # convert iob index to iob string
            decoded_tags_list = iob_index_to_str(predicted_tags)
            # union text as a sequence and convert index to string
            words_list, decoded_texts_list = text_index_to_str(text_segments, mask)
            for idx, (decoded_tags, decoded_texts, image_index, word_list) in enumerate(zip(decoded_tags_list, decoded_texts_list, image_indexs, words_list)):
                # List[ Tuple[str, Tuple[int, int]] ]
                spans = bio_tags_to_spans(decoded_tags, [])
                spans = sorted(spans, key=lambda x: x[1][0])
                bbox = input_data_item['boxes_coordinate'][idx].cpu().numpy().astype(np.int32)
                for entity_name, range_tuple in spans:
                    for b_num, w in enumerate(word_list):
                        if range_tuple[0] in range(*w[0]):
                            boxes_and_transcripts_data[b_num][3] = entity_name
    
    rules = Label_rules(image_size=image.shape[:2])        
    i = 0
    while i <= 2 :
        for idx, box in enumerate(boxes_and_transcripts_data):
            if i == 0 and box[3] == 'other': 
                label, is_total_bool = rules.is_total(boxes_and_transcripts_data, idx)
                if is_total_bool:
                    box[3] = label
                # elif rules.is_product(boxes_and_transcripts_data, idx):
                #     box[3] = 'product'
                elif rules.is_price(boxes_and_transcripts_data, idx):
                    box[3] = 'price'
                else:
                    box[3] = 'other'
            # elif i>0 and box[3] in ['product','price','other','total']:
            elif i>0 and box[3] in ['total','price']:
                label, is_total_bool = rules.is_total(boxes_and_transcripts_data, idx)
                if is_total_bool:
                    box[3] = label
                # elif rules.is_product(boxes_and_transcripts_data, idx):
                #     box[3] = 'product'
                elif rules.is_price(boxes_and_transcripts_data, idx):
                    box[3] = 'price'
                else:
                    box[3] = 'other'
        i += 1

    boxes_and_transcripts_data = np.asarray(boxes_and_transcripts_data)
    # if(len(boxes_and_transcripts_data[(boxes_and_transcripts_data[:,3]=="subtotal") | (boxes_and_transcripts_data[:,3]=="total")]) > 0):
    if(len(boxes_and_transcripts_data[boxes_and_transcripts_data[:,3]=="subtotal"]) > 0) or \
        (len(boxes_and_transcripts_data[boxes_and_transcripts_data[:,3]=="total"]) > 2):
        boxes_and_transcripts_data = Label_rules.get_final_total(boxes_and_transcripts_data)

    boxes_and_transcripts_data = rules.get_final_product_price(boxes_and_transcripts_data)
    
    # y_pred = []
    # img2csv=[]
    # for idx, box in enumerate(boxes_and_transcripts_data):
    #     if box[3] in ['product','price','total','company','address','date']:
    #         cv2.polylines(image, [box[1].reshape((-1, 1, 2))], True, color=(0, 0, 255), thickness=2)
    #         cv2.putText(image, box[3], (box[1][4],box[1][5]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    #     y_pred.append(box[3])
    #     img2csv.append([box[0],*(box[1].tolist()),box[2],box[3]])
    # cv2.imwrite(os.path.join(args.output_folder,save_image),image)
    # df = pd.DataFrame(img2csv)
    # df.to_csv('/home/son/Downloads/weights/test/1111/'+save_image.split('.')[0]+'.tsv', index=False, header=False,
    #             quotechar='',escapechar='\\',quoting=csv.QUOTE_NONE)
    if args.test_mode:
        return boxes_and_transcripts_data, y_pred
    return boxes_and_transcripts_data

