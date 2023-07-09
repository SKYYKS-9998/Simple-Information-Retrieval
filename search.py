import os
import re
from sklearn.feature_extraction.text import CountVectorizer
import math
from collections import defaultdict


class InfoRetrie:
    def __init__(self):
        print("Loading data")
        self.path = 'bbc'      # 数据根路径
        self.dir_list = []      # 存储根路径下所有目录的目录名
        self.txt_name_dict = defaultdict(list)  # 存储所有txt文件名
        self.load_dir(self.path)
        self.data_dict = self.load_data_dict()
        print("Data vectorizing")
        self.bag_vec_dict, self.word_count_dict = self.load_bag_vector()
        print("Generating inverse index")
        self.inverse_index = self.generate_inverse_index()
        print("Loading Complete")

    # 递归获取目录和所有子目录内的txt文件路径和文件名
    def load_dir(self, dir_path):
        cur_dirlist = os.listdir(dir_path)
        for i in cur_dirlist:
            cur_path = dir_path + '\\' + i
            # 是目录，继续调用
            if os.path.isdir(cur_path):
                self.dir_list.append(cur_path)
                self.load_dir(cur_path)
            # 是文件，存储文件名和路径
            else:
                self.txt_name_dict[dir_path].append(i)

    # 获取所有txt文件内容
    def load_data_dict(self):
        data_dict = {}
        for i in range(0, len(self.dir_list)):
            data_dict[self.dir_list[i]] = []
            for j in self.txt_name_dict[self.dir_list[i]]:
                f = open(self.dir_list[i] + '\\' + j, encoding='utf-8')
                text = f.read()
                if len(text) > 0:
                    data_dict[self.dir_list[i]].append(text)
        return data_dict

    # 加载所有文档各自的向量
    def load_bag_vector(self):
        bag = {}
        count = {}
        for i in self.data_dict.keys():
            data_list = self.data_dict[i]
            # 构造向量和计算每个单词出现数
            bag[i] = CountVectorizer(token_pattern='\\b[A-Za-z]+\\b')
            count[i] = bag[i].fit_transform(data_list)
        return bag, count

    # 计算全部文档的倒排索引
    def generate_inverse_index(self):
        # 转换为数组，方便使用
        count_array_dict = {}
        for i in self.word_count_dict.keys():
            count_array_dict[i] = self.word_count_dict[i].toarray()
        # 构造倒排索引
        result = defaultdict(list)
        for t_index in self.data_dict.keys():
            # 取所有存在的单词
            words = self.bag_vec_dict[t_index].get_feature_names_out()
            for index, value in enumerate(self.data_dict[t_index]):
                for i, word in enumerate(words):
                    # 目前文件包含该单词
                    if count_array_dict[t_index][index][i] != 0:
                        # 添加倒排索引节点，包含‘路径 文件名’、单词出现次数和所有出现位置
                        position_list = [m.span() for m in re.finditer(r'\b' + word + r'\b', value)]
                        result[word].append((t_index + ' ' + str(index), count_array_dict[t_index][index][i], position_list))
        return result

    # 计算搜索内容和结果文件内容的相似度，夹角余弦相关度
    def get_similarity(self, a, b):
        dot = 0
        sqrt_a = 0
        sqrt_b = 0
        for i in range(len(a)):
            dot += a[i] * b[i]
            sqrt_a += a[i] * a[i]
            sqrt_b += b[i] * b[i]
        sqrt_a = math.sqrt(sqrt_a)
        sqrt_b = math.sqrt(sqrt_b)
        if dot == 0 or sqrt_a == 0 or sqrt_b == 0:
            return 0
        return dot / (sqrt_a * sqrt_b)

    # 搜索
    def do_search(self, search_str):
        in_indexs = []
        freq = defaultdict(int)
        # 搜索内容按空格分词
        search_words = search_str.split(' ')
        for word in search_words:
            if self.inverse_index[word]:
                # 找出对应的索引，记录出现次数
                in_indexs.append(self.inverse_index[word].copy())
                word_count = 0
                for i in self.inverse_index[word]:
                    word_count += i[1]
                freq[word] = word_count
        result_dict = {}
        for i in in_indexs:
            for j in i:
                # j = [文件名，出现次数，[出现位置]]
                file_name = j[0]
                word_count = j[1]
                location_list = j[2]
                if j[0] not in result_dict:
                    text_name = file_name.split()
                    item = Result(text_name[0], text_name[1], self.data_dict[text_name[0]][int(text_name[1])])
                    item.freq += word_count
                    item.location.extend(location_list)
                    result_dict[file_name] = item
                else:
                    result_dict[file_name].freq += word_count
                    result_dict[file_name].location.extend(location_list)

        for key, value in result_dict.items():
            search_vec = CountVectorizer(vocabulary=self.bag_vec_dict[value.path].get_feature_names_out()).fit_transform([search_str]).toarray()
            value.similarity = self.get_similarity(search_vec[0], self.word_count_dict[value.path][int(value.name)].A[0])

        result_list = [i for i in result_dict.values()]
        result_list.sort(key=lambda x: -x.similarity)
        return result_list


class Result:
    def __init__(self, path, name, text):
        self.path = path    # 文件路径
        self.name = name    # 文件名
        self.text = text    # 文件内容
        self.freq = 0       # 检索内容出现次数
        self.location = []    # 检索内容出现位置
        self.similarity = 0.0   # 相关度

    def __str__(self):
        s = "Directory: " + self.path + \
            "\nTXT file name: " + self.name + \
            "\nAppearance counts: " + str(self.freq) + \
            "\nSimilarity: " + str(self.similarity) + \
            "\nLocations:\n"
        for j in self.location:
            s += "> ..." + self.text[max(0, j[0] - 50):j[0] + 50] + "...\n"
        return s
