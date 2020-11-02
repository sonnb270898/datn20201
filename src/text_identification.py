import torch
from tqdm import tqdm
from pathlib import Path

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
except ImportError:
    from src.parse_config import ConfigParser
    import src.identification.model.pick as pick_arch_module
    from src.identification.data_utils.pick_dataset import PICKDataset, TestingDataset
    from src.identification.data_utils.pick_dataset import BatchCollateFn
    from src.identification.utils.util import iob_index_to_str, text_index_to_str
    from src.identification.utils.class_utils import set_vocab
    from src.opt import get_config

import re
import cv2
import os
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt     
from sklearn.metrics import confusion_matrix,accuracy_score
import pylab as pl

args = get_config()
device = torch.device("cuda:0" if torch.cuda.is_available() else 'cpu')

_class_name = ['product','price','total','other']
_price_pattern = r"\d+(\s*(\\,)?\.?\s*)\d+"
_product_pattern = r"([A-za-z]{3,})+"

W,H = (480,960)

def visual_confusion_matrix(y_true,y_pred):
    print(accuracy_score(y_true,y_pred))
    cm = confusion_matrix(y_true, y_pred, labels=_class_name)
    print(cm)
    ax= plt.subplot()
    sns.heatmap(cm, annot=True, ax = ax); #annot=True to annotate cells

    # labels, title and ticks
    ax.set_xlabel('Predicted labels');ax.set_ylabel('True labels'); 
    ax.set_title('Confusion Matrix'); 
    ax.xaxis.set_ticklabels(_class_name); ax.yaxis.set_ticklabels(_class_name);
    plt.show()

def find_neighbor_label(boxes, index, label):
    i = index-1
    j = index+1
    dis_i = 99999
    dis_j = 99999
    boxes_len = len(boxes)
    while i>=0:
        if boxes[i][3] == label:
            break
        i-=1
    while j<boxes_len:
        if boxes[j][3] == label:
            break
        j+=1
    if i != -1:
        dis_i = abs(boxes[i][1][1] - boxes[index][1][1]) 
    if j != boxes_len:
        dis_j = abs(boxes[j][1][1] - boxes[index][1][1])
    
    if i == -1 and j == boxes_len:
        return -1
    if dis_i - dis_j > 0:
        return j
    return i

min_distance_price_price_x = 50
min_distance_product_price_x = 200
min_distance_total_total_x = 100

def is_price(boxes, index):
    result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
    if result and (boxes[index][1][0] > W/2) and (boxes[index][1][1]) > H/4 and (boxes[index][1][1]) < 3*H/4:
        if result.group(1) != '':
            boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')
        #check distance product_product & product_price(theo x va y) 
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])+20):
                return True
        elif product_nb != -1 and price_nb == -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])+20):
                return True
        elif  product_nb == -1:
            return True   
    return False

def is_product(boxes, index):
    result = re.search(_product_pattern, boxes[index][2])
    if  result and (boxes[index][1][0] < W/2) and (boxes[index][1][1]) > H/4:
        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')
        #check distance product_product & product_price(theo x va y)
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])+20):
                return True
        elif product_nb == -1 and price_nb != -1:
            if  (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])+20):
                return True
        elif price_nb == -1:
            return True
    return False

def is_total(boxes, index):
    result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
    if result and (boxes[index][1][0] > W/2) and (boxes[index][1][1]) > H/4:
        if result.group(1) != '':
            boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

        price_nb = find_neighbor_label(boxes,index,'price')
        total_nb = find_neighbor_label(boxes,index,'total')
        #check distance total_total & total_price(theo x va y) 
        if total_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[total_nb][1][0]) >= min_distance_total_total_x) and \
                (abs(boxes[index][1][1] -  boxes[total_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])/2):
                return True
    return False

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

def extract_information(image, boxes_and_transcripts_data, pick_model, save_image):
    # setup dataset and data_loader instances
    test_dataset = TestingDataset(image=image,
                                  boxes_and_transcripts_data=boxes_and_transcripts_data,
                                  ignore_error=False,
                                )
    test_data_loader = DataLoader(test_dataset, batch_size=1, shuffle=False,
                                  num_workers=1, collate_fn=BatchCollateFn(training=False))

    # setup output path
    output_path = Path(args.output_folder)
    output_path.mkdir(parents=True, exist_ok=True)

    #y_true 
    y_true = []
    y_pred = []
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
                # y_true
                # y_true += input_data_item['labels'][idx]
                # _y_p = np.full_like(input_data_item['labels'][idx],'other')
                bbox = input_data_item['boxes_coordinate'][idx].cpu().numpy().astype(np.int32)
                entities = []  # exists one to many case
                for entity_name, range_tuple in spans:
                    for b_num, w in enumerate(word_list):
                        if range_tuple[0] in range(*w[0]):
                            # entity = dict(entity_name=entity_name,
                            #             text=''.join(decoded_texts[range_tuple[0]:range_tuple[1] + 1]))
                            entity = dict(entity_name=entity_name,
                            text=w[1],
                            box=b_num
                            )
                            entities.append(entity)
                            # if entity_name in ['date','company','address']:
                            #     _y_p[b_num] = 'other'
                            # else:
                            #     _y_p[b_num] = entity_name
                            boxes_and_transcripts_data[b_num][3] = entity_name
                            # cv2.polylines(image, [bbox[b_num].reshape((-1, 1, 2))], True, color=(0, 0, 255), thickness=2)
                            # cv2.putText(image, entity_name, (bbox[b_num][4],bbox[b_num][5]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
                # y_pred = np.concatenate((y_pred,_y_p))
                # result_file = output_path.joinpath(Path(test_dataset.files_list[image_index]).stem + '.txt')
                # result_file = output_path.joinpath(Path('result.txt'))
                # with result_file.open(mode='w') as f:
                #     for item in entities:
                #         f.write('{}\t{}\t{}\n'.format(item['entity_name'], item['text'],item['box']))
                
                # cv2.imwrite(os.path.join(args.output_folder,'result.jpg'),image)
    # visual_confusion_matrix(y_true,y_pred.tolist())
    i = 0
    while i <= 2 :
        for idx, box in enumerate(boxes_and_transcripts_data):
            if box[3] in ['product','price','other']:
                if is_price(boxes_and_transcripts_data, idx):
                    box[3] = 'price'
                elif is_product(boxes_and_transcripts_data, idx):
                    box[3] = 'product'
                elif is_total(boxes_and_transcripts_data, idx):
                    box[3] = 'total'
                else:
                    box[3] = 'other'
        i += 1
    for idx, box in enumerate(boxes_and_transcripts_data):
        if box[3] in ['product','price','total']:
            cv2.polylines(image, [box[1].reshape((-1, 1, 2))], True, color=(0, 0, 255), thickness=2)
            cv2.putText(image, box[3], (box[1][4],box[1][5]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0), 1, cv2.LINE_AA)
    cv2.imwrite(os.path.join(args.output_folder,save_image),image)
    return ''

if __name__ == '__main__':
    identifier = load_identifier()
    image = cv2.imread("/home/son/Desktop/datn20201/resource/img/1029-receipt.jpg")
    image = cv2.resize(image, (480, 960))
    extract_information(image,boxes,identifier)
