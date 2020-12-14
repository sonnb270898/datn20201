import re
import datetime 
from dateutil.parser import parse

# _price_pattern = r"\d+(\s*(\\,)?\.?\s*)\d+"
_price_pattern = r"\d+(\s*(\\,|\.|[a-zA-Z]|;|'|\"|\s+){1,}\s*)\d+"
_product_pattern = r"([A-za-z]{2,})+"
_date_pattern = r"(\d+(\s*[/\-\.]\s*)\d+(\s*[/\-\.]\s*)\d+)"
_suffix_price_pattern = r"((\\,|\.|[a-zA-Z]|;|'|\"|\s+){1,}\s*)\d+"

total_synonym = ['total','grand','amt','balance','due']
tax_subtotal = ['subtotal','tax','items','qty','subtotai','sub-total','sub-totai','discount','total']

min_distance_price_price_x = 50
min_distance_product_price_x = 100
min_distance_total_total_x = 50
min_distance_total_price_x = 100

class Label_rules:
    def __init__(self, image_size=(480,960)):
        self.H, self.W = image_size
    
    def find_neighbor_label(self, boxes, index, label):
        i = index-1
        j = index+1
        dis_i = 99999
        dis_j = 99999
        boxes_len = len(boxes)
        while i>=0:
            if (boxes[i][3] == label):
                if label == 'product' and boxes[i][1][0] < self.W/2:
                    break
                elif label == 'price' and boxes[i][1][0] > self.W/2:
                    break
                elif label == 'total' and re.search(_product_pattern, boxes[i][2], re.IGNORECASE):
                    break
            i-=1
        while j<boxes_len:
            if (boxes[j][3] == label):
                if label == 'product' and boxes[j][1][0] < self.W/2:
                    break
                elif label == 'price' and boxes[j][1][0] > self.W/2:
                    break
                elif label == 'total' and re.search(_product_pattern, boxes[j][2], re.IGNORECASE):
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

    def first_box_in_line(self, boxes, index):
        i = index
        while index > 0:
            if  boxes[index][1][0] > boxes[index-1][1][0] and \
                abs(boxes[index-1][1][1] - boxes[i][1][1]) < abs(boxes[i][1][1] - boxes[i][1][-1]):
                index-=1
            else:
                return index
        return 1
    def is_price(self, boxes, index):
        check_price = re.search(_suffix_price_pattern, boxes[index][2], re.IGNORECASE)
        result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
        if boxes[index][3]=='price' and check_price and check_price.end() == len(boxes[index][2]) and (boxes[index][1][0] > self.W/2):
            if boxes[index][2].startswith('.'):
                boxes[index][2] = '0' + boxes[index][2].replace(check_price.group(1),'.')
                return True
            elif result:
                boxes[index][2] = boxes[index][2].replace(result.group(1),'.')
                return True 

        result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
        if result and (boxes[index][1][0] > self.W/2):
            boxes[index][2] = boxes[index][2].replace(result.group(1),'.')
            # if result.group(1) != '':
            #     boxes[index][2] = boxes[index][2].replace(result.group(1),'.')
            price_nb = self.find_neighbor_label(boxes, index, 'price')
            product_nb = self.find_neighbor_label(boxes, index, 'product')

            fb = self.first_box_in_line(boxes, index)
            is_in_total_region = any([True if i in boxes[fb][2].lower() else False for i in tax_subtotal])
            if boxes[index][3] == 'other':
                if  is_in_total_region:
                    return False
                if  abs(boxes[fb][1][0] - boxes[product_nb][1][0]) > min_distance_price_price_x or\
                    (boxes[fb-1][3] == 'price' and boxes[fb][3] == 'other'):
                    return False

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
            elif product_nb == -1:
                return False
        return False

    def is_product(self, boxes, index):
        result = re.search(_product_pattern, boxes[index][2], re.IGNORECASE)
        is_in_total_region = any([True if i in boxes[index][2].lower() else False for i in tax_subtotal])
        if result and (boxes[index][1][0] < self.W/2) and not is_in_total_region:
            has_price = max([x.end() for x in re.finditer(_price_pattern, boxes[index][2], re.IGNORECASE)]+[0])
            if has_price and has_price >= len(boxes[index][2]) and boxes[index][1][2] > self.W/2:
                return True
            price_nb = self.find_neighbor_label(boxes,index,'price')
            product_nb = self.find_neighbor_label(boxes,index,'product')
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
        return False

    def is_total(self, boxes, index):
        result = re.search(_price_pattern, boxes[index][2], re.IGNORECASE)
        if result and boxes[index][1][2] > self.W/2:
            boxes[index][2] = boxes[index][2].replace(result.group(1),'.')

        if not result and boxes[index][3] == 'total':
            # boxes[index][3] = 'subtotal'
            return 'total', True

        if result and (boxes[index][1][1]) > self.H/4:
            total_nb = self.find_neighbor_label(boxes,index,'total')
            #check distance total_total & total_price(theo x va y) 
            if total_nb != -1:
                has_total = re.search(_price_pattern, boxes[total_nb][2], re.IGNORECASE)
                if has_total and has_total.end() == len(boxes[total_nb][2]):
                    return 'other',False
                elif (abs(boxes[index][1][0] -  boxes[total_nb][1][0]) >= min_distance_total_total_x) and \
                    (abs(boxes[index][1][1] -  boxes[total_nb][1][1]) <= abs(boxes[total_nb][1][1] -  boxes[total_nb][1][-1])*0.75):
                    return 'total', True
            elif total_nb == -1 and index > 1:
                if any([True if t_nym in boxes[index][2].lower() else False for t_nym in total_synonym]):
                    return 'subtotal', True
                elif any([True if t_nym in boxes[index-1][2].lower() else False for t_nym in total_synonym]):
                    if abs(boxes[index-1][1][0] - boxes[index][1][0]) >= min_distance_total_total_x \
                        or (boxes[index-1][3] == 'total'):
                        boxes[index-1][3] = 'subtotal'
                        return 'subtotal', True
                elif any([True if t_nym in boxes[index-2][2].lower() else False for t_nym in total_synonym]):
                    if abs(boxes[index-2][1][0] - boxes[index][1][0]) >= min_distance_total_total_x \
                        or (boxes[index-1][3] == 'total') :
                        boxes[index-2][3] = 'subtotal'
                        return 'subtotal', True
        return 'other', False

    @staticmethod
    def get_final_total(boxes):
        idx = ((boxes[:,3]=="subtotal") | (boxes[:,3]=="total")).nonzero()[0]
        total_max, id_max = (0,-1)
        id_max_eq = -1
        for i in idx:
            result = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
            if result:
                tmp = result.group(1).replace(' ','')
                if float(tmp) >= total_max:
                    if float(tmp) == total_max:
                        id_max_eq = id_max
                    total_max, id_max = (float(tmp), i)
            boxes[i][3] = 'other'
        if id_max != -1:
            current_i = idx.tolist().index(id_max) - 1
            if id_max_eq != -1:
                tmp = idx.tolist().index(id_max_eq) - 1
                cime_total_label = any([True if i in boxes[idx[current_i]][2].lower() else False for i in total_synonym])
                cim_total_label = any([True if i in boxes[idx[tmp]][2].lower() else False for i in total_synonym])
                if cime_total_label:
                    pass
                elif cim_total_label:
                    id_max = id_max_eq
                    current_i = idx.tolist().index(id_max) - 1
            boxes[id_max][3] = 'total'
            while current_i > -1:
                pre_box = boxes[idx[current_i]]
                # get label_box total in same line
                if abs(pre_box[1][1] - boxes[id_max][1][1]) <= 15:
                    boxes[idx[current_i]][3] = 'total'
                current_i -= 1
        return boxes

    def get_final_product_price(self, boxes):
        total_nb = self.find_neighbor_label(boxes, 0, 'total')
        if total_nb != -1:
            for box in boxes[total_nb:]:
                if box[3] in ['product','price']:
                    box[3] = 'other'  
        return boxes
    
def convert_result_to_json(boxes):
    result = {}
    result['pp'] = []
    product = []
    price = []
    boxes_len = len(boxes)
    product_value = ''
    for i in range(boxes_len):
        if boxes[i][3] == 'product':
            __price = re.search(_price_pattern, boxes[i][2], re.IGNORECASE)
            if __price and __price.end() == len(boxes[i][2]):
                result['pp'].append((' '.join([p[1] for p in product]),price[0][1]))
                product = []
                price = []
                product.append((i, boxes[i][2][:__price.start()]))
                price.append((i, __price.group()))
            else:
                product.append((i, boxes[i][2]))
            if (i+1 < boxes_len and boxes[i+1][3] == 'price'):
                if len(price) != 0:
                    for j, (idx, p) in enumerate(product):
                        if abs(boxes[idx][1][1] - boxes[i][1][1]) < abs(boxes[i][1][-1] - boxes[i][1][1])/2:
                            break
                    for p in product[:j]:
                        product_value = product_value + ' ' + p[1]
                    result['pp'].append((product_value, price[0][1]))
                    del product[:j]
                    del price[0]
                    product_value = ''
                else:
                    for j, (idx, p) in enumerate(product[:-1]):
                        if boxes[idx][1][1] - boxes[i][1][1] < -abs(boxes[i][1][-1] - boxes[i][1][1])/3:           
                            del product[j]  
        elif boxes[i][3] == 'price':
            __price = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
            price.append((i, __price.group()))
        elif boxes[i][3] == 'total':
            total = re.search(r'(\d+\s*\.\s*\d+)',boxes[i][2],re.IGNORECASE)
            if total:
                result['total'] = total.group(1)
        elif boxes[i][3] == 'date':
            result['date'] = search_date(boxes[i][2])
        elif boxes[i][3] == 'company':
            result['company'] = result.get('company','') + boxes[i][2]
    if len(price) != 0:
        result['pp'].append((' '.join([p[1] for p in product]),price[0][1]))
    if result.get('date','') == '':
        result['date'] = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%fZ")
    return result

def search_date(text):
    date = ''
    try:
        date = parse(text, fuzzy_with_tokens=True)[0].strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return date
    except:
        res = re.search(_date_pattern, text, re.IGNORECASE)
        if res:
            date = res.group(1).replace(' ','')
            return parse(date).strftime("%Y-%m-%dT%H:%M:%S.%fZ")
        return date
    return date

if __name__ == '__main__':

    boxes = [[1, [222,  70, 466,  70, 466, 119, 222, 119], 'Katana Sushi', 'company']
    ,[1, [192, 119, 496, 119, 496, 166, 192, 166], '2818 Hewitt Ave', 'address']
    ,[1, [171, 160, 516, 160, 516, 213, 171, 213], 'Everett\\, wa 98201', 'address']
    ,[1, [230, 209, 477, 209, 477, 263, 230, 263], '425-512-9361', 'other']
    ,[1, [334, 267, 437, 267, 437, 300, 334, 300], 'xxxxx', 'other']
    ,[1, [ 37, 363, 393, 363, 393, 405,  37, 405], 'Server: Michael c', 'other']
    ,[1, [330, 393, 672, 393, 672, 440, 330, 440], '05/11/18 8:47 PM', 'date']
    ,[1, [ 30, 459, 227, 459, 227, 499,  30, 499], 'Check #93', 'other']
    ,[1, [499, 452, 675, 452, 675, 494, 499, 494], 'Table D2', 'other']
    ,[1, [ 28, 553, 331, 553, 331, 601,  28, 601], 'Hamachi Collar', 'product']
    ,[1, [541, 550, 679, 550, 679, 592, 541, 592], '$12.00', 'price']
    ,[1, [25, 607, 325, 607, 325, 651, 25, 651], 'Mega Poke Bowl', 'product']
    ,[1, [543, 602, 679, 602, 679, 646, 543, 646], '$17.00', 'price']
    ,[1, [ 25, 660, 178, 660, 178, 706,  25, 706], 'Hamachi', 'product']
    ,[1, [238, 656, 392, 656, 392, 704, 238, 704], 'Sashimi', 'product']
    ,[1, [543, 653, 682, 653, 682, 698, 543, 698], '$12.00', 'price']
    ,[1, [ 24, 713, 162, 713, 162, 763,  24, 763], 'Maguro', 'product']
    ,[1, [215, 712, 370, 712, 370, 754, 215, 754], 'Sashimi', 'product']
    ,[1, [543, 707, 682, 707, 682, 752, 543, 752], '$11.00', 'price']
    ,[1, [ 28, 766, 161, 766, 161, 808,  28, 808], 'Salmon', 'product']
    ,[1, [217, 764, 370, 764, 370, 808, 217, 808], 'Sashimi', 'product']
    ,[1, [543, 761, 682, 761, 682, 803, 543, 803], '$10.00', 'price']
    ,[1, [ 30, 815, 375, 815, 375, 862,  30, 862], '3 Sockeye Salmon', 'product']
    ,[1, [431, 815, 585, 815, 585, 857, 431, 857], 'Sashimi', 'product']
    ,[1, [546, 857, 684, 857, 684, 902, 546, 902], '$36.00', 'price']
    ,[1, [ 23, 925, 372, 925, 372, 970,  23, 970], 'Hamachi Japapeno', 'product']
    ,[1, [548, 921, 689, 921, 689, 965, 548, 965], '$12.00', 'price']
    ,[1, [  21,  977,  307,  977,  307, 1024,   21, 1024], 'Salmon Collar', 'product']
    ,[1, [ 550,  977,  691,  977,  691, 1021,  550, 1021], '$10.00', 'price']
    ,[1, [  18, 1033,  175, 1033,  175, 1078,   18, 1078], 'Escolar', 'product']
    ,[1, [ 234, 1033,  391, 1033,  391, 1078,  234, 1078], 'Sashimi', 'product']
    ,[1, [ 550, 1031,  693, 1031,  693, 1078,  550, 1078], '$11.00', 'price']
    ,[1, [  14, 1146,  194, 1146,  194, 1190,   14, 1190], 'Subtotal', 'other']
    ,[1, [ 532, 1146,  698, 1146,  698, 1192,  532, 1192], '$131.00', 'other']
    ,[1, [  14, 1202,   86, 1202,   86, 1246,   14, 1246], 'Tax', 'other']
    ,[1, [ 555, 1204,  698, 1204,  698, 1253,  555, 1253], '$12.71', 'other']
    ,[1, [  12, 1257,  125, 1257,  125, 1306,   12, 1306], 'Total', 'total']
    ,[1, [ 534, 1263,  700, 1263,  700, 1310,  534, 1310], '$143.71', 'total']
    ,[1, [ 496, 1304,  692, 1304,  692, 1426,  496, 1426], '15754', 'other']
    ,[1, [ 259, 1369,  452, 1369,  452, 1411,  259, 1411], 'XXXXXXXX', 'other']
    ,[1, [  71, 1418,  644, 1418,  644, 1476,   71, 1476], 'Thank You for your visit.', 'other']]

    print(convert_result_to_json(boxes))
    date = "20/1/1992"
    print(search_date(date)) 





