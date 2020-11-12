import re

# _price_pattern = r"\d+(\s*(\\,)?\.?\s*)\d+"
_price_pattern = r"\d+(\s*(\\,|\.|[a-zA-Z]|\s+){1,}\s*)\d+"
_product_pattern = r"([A-za-z]{2,})+"

min_distance_price_price_x = 50
min_distance_product_price_x = 200
min_distance_total_total_x = 100
min_distance_total_price_x = 100
W,H = (480,960)

def find_neighbor_label(boxes, index, label):
    i = index-1
    j = index+1
    dis_i = 99999
    dis_j = 99999
    boxes_len = len(boxes)
    while i>=0:
        if (boxes[i][3] == label):
            if label == 'product' and boxes[i][1][0] < W/2:
                break
            elif label == 'price' and boxes[i][1][0] > W/2:
                break
            elif label == 'total' and boxes[i][1][0] < 225:
                break
        i-=1
    while j<boxes_len:
        if (boxes[j][3] == label):
            if label == 'product' and boxes[j][1][0] < W/2:
                break
            elif label == 'price' and boxes[j][1][0] > W/2:
                break
            elif label == 'total' and boxes[j][1][0] < 225:
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

def is_price(boxes, index):
    result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
    if result:
        boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

    if result and (boxes[index][1][0] > W/2) and (boxes[index][1][1]) > H/4 and (boxes[index][1][1]) < 3*H/4:
        # if result.group(1) != '':
        #     boxes[index][2] = boxes[index][2].replace(result.group(1),'.')
        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')
        #check distance product_product & product_price(theo x va y) 
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][2] -  boxes[price_nb][1][2]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[product_nb][1][1] -  boxes[product_nb][1][-1])+15):
                return True
        elif product_nb != -1 and price_nb == -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) >= min_distance_product_price_x) and\
                (abs(boxes[index][1][1] -  boxes[product_nb][1][1]) <= abs(boxes[product_nb][1][1] -  boxes[product_nb][1][-1])+15):
                return True
        elif  product_nb == -1:
            return False   
    return False

def is_product(boxes, index):
    result = re.search(_product_pattern, boxes[index][2], re.IGNORECASE)
    if  result and (boxes[index][1][0] < W/2) and (boxes[index][1][1]) > H/4:
        price_nb = find_neighbor_label(boxes,index,'price')
        product_nb = find_neighbor_label(boxes,index,'product')
        #check distance product_product & product_price(theo x va y)
        if product_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][0] -  boxes[product_nb][1][0]) <= min_distance_price_price_x) and \
                (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[price_nb][1][1] -  boxes[price_nb][1][-1])+15):
                return True
        elif product_nb == -1 and price_nb != -1:
            if  (abs(boxes[index][1][0] -  boxes[price_nb][1][0]) >= min_distance_product_price_x) and \
                (abs(boxes[index][1][1] -  boxes[price_nb][1][1]) <= abs(boxes[price_nb][1][1] -  boxes[price_nb][1][-1])+15):
                return True
        elif price_nb == -1:
            return False
    return False

total_synonym = ['total','grand','amt', 'balance']

def is_total(boxes, index):
    result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
    if result:
        boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

    if not result and boxes[index][3] == 'total':
        # boxes[index][3] = 'subtotal'
        return 'total', True

    if result and (boxes[index][1][0] > W/3) and (boxes[index][1][1]) > H/4:
        price_nb = find_neighbor_label(boxes,index,'price')
        total_nb = find_neighbor_label(boxes,index,'total')
        #check distance total_total & total_price(theo x va y) 
        if total_nb != -1 and price_nb != -1:
            if (abs(boxes[index][1][2] -  boxes[price_nb][1][2]) <= min_distance_total_price_x) and \
                (abs(boxes[index][1][0] -  boxes[total_nb][1][0]) >= min_distance_total_total_x) and \
                (abs(boxes[index][1][1] -  boxes[total_nb][1][1]) <= abs(boxes[index][1][1] -  boxes[index][1][-1])/2):
                return 'total', True
        elif total_nb == -1 and index > 1:
            if any([True if t_nym in boxes[index][2].lower() else False for t_nym in total_synonym]):
                return 'subtotal', True
            elif any([True if t_nym in boxes[index-1][2].lower() else False for t_nym in total_synonym]):
                if (boxes[index-1][1][0] < W/2 and abs(boxes[index-1][1][0] - boxes[index][1][0]) >= min_distance_total_total_x) \
                    or (boxes[index-1][3] == 'total'):
                    boxes[index-1][3] = 'subtotal'
                    return 'subtotal', True
            elif any([True if t_nym in boxes[index-2][2].lower() else False for t_nym in total_synonym]):
                if (boxes[index-2][1][0] < W/2 and abs(boxes[index-2][1][0] - boxes[index][1][0]) >= min_distance_total_total_x) \
                    or (boxes[index-1][3] == 'total') :
                    boxes[index-2][3] = 'subtotal'
                    return 'subtotal', True
    return 'other', False

def get_final_total(boxes):
    idx = ((boxes[:,3]=="subtotal") | (boxes[:,3]=="total")).nonzero()[0]
    total_max, id_max = (0,-1)
    for i in idx:
        result = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
        if result:
            if float(result.group(1)) >= total_max:
                total_max, id_max = (float(result.group(1)), i)
        boxes[i][3] = 'other'
    if id_max != -1:
        current_i = idx.tolist().index(id_max) - 1
        boxes[id_max][3] = 'total'
        while current_i > -1:
            pre_box = boxes[idx[current_i]][1]
            # get label_box total in same line
            if abs(pre_box[1] - boxes[id_max][1][1]) <= 20:
                boxes[idx[current_i]][3] = 'total'
            current_i -= 1
    return boxes 
    




