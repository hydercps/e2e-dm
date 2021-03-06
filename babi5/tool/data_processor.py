# coding:utf-8

'''
  This script is for data pre-processing.
  Dataset introduction:
    Number of restaurants: 113
    Number of cuisine: 24
    Number of price: 3 (expensive, moderate, cheap)
    Number of locations: 5 (south, west, centre, north, east)

  Created on Aug 7, 2017
  Author: qihu@mobvoi.com
'''

import data_loader as dl
import copy

# Save the attributes list in knowledge base to plain txt
def save_kb_value(kb_path):
    cuisine_path = 'babi5/cuisine.txt'
    location_path = 'babi5/location.txt'
    price_path = 'babi5/price.txt'
    post_code_path = 'babi5/number.txt'
    phone_path = 'babi5/phone.txt'
    address_path = 'babi5/address.txt'
    rating_path = 'babi5/rating.txt'
    with open(kb_path) as f:
        lines = f.readlines()
    f_cuisine = open(cuisine_path, 'w')
    f_location = open(location_path, 'w')
    f_price = open(price_path, 'w')
    f_number = open(post_code_path, 'w')
    f_phone = open(phone_path, 'w')
    f_address = open(address_path, 'w')
    f_rating = open(rating_path, 'w')
    f_values = {'R_cuisine': f_cuisine,
                'R_location': f_location,
                'R_price': f_price,
                'R_number': f_number,
                'R_address': f_address,
                'R_phone': f_phone,
                'R_rating': f_rating}
    names = []
    values = {'R_cuisine': [],
              'R_location': [],
              'R_price': [],
              'R_number': [],
              'R_address': [],
              'R_phone': [],
              'R_rating': []}
    num_line = len(lines)
    print num_line
    for i in range(num_line):
        line = lines[i].strip('\n').split(' ')
        attribute = line[2]
        value = line[3]
        if value not in values[attribute]:
            values[attribute].append(value)
    for attr in values.keys():
        for v in values[attr]:
            f_values[attr].write('%s\n' % v)

    f_cuisine.close()
    f_location.close()
    f_price.close()
    f_number.close()
    f_phone.close()
    f_address.close()
    f_rating.close()
    return names, values


# Save the vocabulary list into a plain txt file
def save_vocab(data_path, kb_path):
    vocab_path = 'babi5/data/all_vocab.txt'
    names, values, val2attr, entities = dl.read_kb_value(kb_path)
    usr_list, sys_list, api_list = dl.read_dialog(data_path)

    vocab_dict = {}
    # print val2attr
    usr_list = dl.flatten_2D(usr_list)
    sys_list = dl.flatten_2D(sys_list)
    num_turn = len(usr_list)
    print len(usr_list), len(sys_list)
    for i in range(num_turn):
        print i
        sentence = ('%s %s' % (usr_list[i], sys_list[i])).split(' ')
        for word in sentence:
            if word in val2attr.keys():
                word = val2attr[word]
            if word in names:
                word = 'R_name'
            if word in vocab_dict.keys():
                vocab_dict[word] = vocab_dict[word]+1
            else:
                vocab_dict[word] = 1
    items = vocab_dict.items()
    items = sorted(items, lambda x, y: cmp(x[1], y[1]), reverse=True)
    with open(vocab_path, 'w') as f:
        for item in items:
            print item[0]
            f.write('%s %d\n' % item)


# check if a sentence is api_call
def get_api_call(s):
    s = s.strip('\n').split(' ')
    hotword = s[0]
    if hotword == 'api_call':
        return s[1:]
    else:
        return []


def save_diff_sys_resp(data_path, kb_path):
    save_path = 'babi5/data/template/sys_resp.txt'
    sys_resp_list = []
    names, values, val2attr, entities = dl.read_kb_value(kb_path)
    # print names
    with open(data_path) as f:
        lines = f.readlines()
    f = open(save_path, 'w')
    num_line = len(lines)
    for i in range(num_line):
        line = lines[i].strip('\n').split('\t')
        if len(line) < 2:
            continue
        sys_resp = line[1]
        sys_word = sys_resp.split(' ')
        num_word = len(sys_word)
        for j in range(num_word):
            word = sys_word[j]
            if word in val2attr:
                sys_word[j] = val2attr[word]
            if word in names:
                sys_word[j] = 'R_name'
        s = ' '.join(sys_word)
        if s in sys_resp_list:
            continue
        sys_resp_list.append(s)
    sys_resp_list.sort()
    for s in sys_resp_list:
        f.write('%s\n' % s)
    f.close()
    return 0


def sort_sentence(data_path):
    save_path = 'data/template/sys_resp_templete_2_sorted.txt'
    s_list = []
    with open(data_path) as f:
        lines = f.readlines()
    f = open(save_path, 'w')
    num_line = len(lines)
    for i in range(num_line):
        s = lines[i]
        s_list.append(s)
    s_list.sort()
    for s in s_list:
        f.write(s)
    f.close()


# Split all dialogs by api call, so that each sample will have a paragraph and an api_call label
def split_api(data_path):
    usr_path = './data/tracker_usr_data.txt'
    sys_path = './data/tracker_sys_data.txt'
    label_path = './data/tracker_label_data.txt'
    usr_list = []
    sys_list = []
    label_list = []
    usr_tmp_list = []
    sys_tmp_list = []
    with open(data_path) as f:
        lines = f.readlines()
    num_line = len(lines)
    f_usr = open(usr_path, 'w')
    f_sys = open(sys_path, 'w')
    f_label = open(label_path, 'w')
    for i in range(num_line):
        line = lines[i].strip('\n').split('\t')
        if len(line) == 1 and len(line[0]) == 0:
            usr_tmp_list = []
            sys_tmp_list = []
            continue
        if len(line) == 1:
            continue
        if line[1].split(' ')[0] == 'api_call':
            labels = line[1].split(' ')
            label_dict = {
                'cuisine': labels[1],
                'location': labels[2],
                'number': labels[3],
                'price': labels[4]
            }
            label_list.append(label_dict)
            usr_list.append(copy.deepcopy(usr_tmp_list))
            sys_list.append(copy.deepcopy(sys_tmp_list))
            continue
        usr_tmp_list.append(line[0].split(' ', 1)[1])
        sys_tmp_list.append(line[1])
    num_sample = len(label_list)
    # print num_sample, len(usr_list), len(sys_list)
    # print len(usr_list[1])
    for i in range(num_sample):
        num_usr_turn = len(usr_list[i])
        num_sys_turn = len(sys_list[i])
        for j in range(num_usr_turn):
            usr_utc = '%s\n' % usr_list[i][j]
            f_usr.write(usr_utc)
        for j in range(num_sys_turn):
            sys_utc = '%s\n' % sys_list[i][j]
            f_sys.write(sys_utc)
        label_str = '%s %s %s %s\n' % (label_list[i]['cuisine'],
                                       label_list[i]['location'],
                                       label_list[i]['number'],
                                       label_list[i]['price'])
        f_label.write(label_str)
        f_usr.write('\n')
        f_sys.write('\n')

    # print usr_list[1]
    f_usr.close()
    f_sys.close()
    f_label.close()


if __name__ == '__main__':
    all_path = 'data/dialog-babi-task5-full-dialogs-all.txt'
    trn_path = 'data/dialog-babi-task5-full-dialogs-trn.txt'
    dev_path = 'data/dialog-babi-task5-full-dialogs-dev.txt'
    tst_path = 'data/dialog-babi-task5-full-dialogs-tst.txt'
    kb_path = 'data/dialog-babi-kb-all.txt'
    # save_kb_value(kb_path)
    # save_vocab(all_path, kb_path)
    # save_diff_sys_resp(all_path, kb_path)
    # sort_sentence('data/template/sys_resp_template_2.txt')
    # save_ask(tst_path)
    split_api(dev_path)