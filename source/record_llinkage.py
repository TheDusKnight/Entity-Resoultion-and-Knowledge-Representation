# %%
# initialization
import os
import csv
from datetime import datetime
import pandas as pd
from IPython.display import display
import rltk

# You can use this tokenizer in case you need to manipulate some data
tokenizer = rltk.CrfTokenizer()


# %%
# df_IMDB = pd.read_csv('../movies2/csv_files/imdb_csv_clean.csv', parse_dates=False)
# print(df_IMDB.head(5))


# TODO: is data cleaning ok?
class IMDBRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = "IMDB"

    @rltk.cached_property
    def id(self):
        return self.raw_object['ID']

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['name']
        # return self.raw_object.get('name', '')

    @rltk.cached_property
    def name_tokens(self):
        return set(tokenizer.tokenize(self.name_string))

    @rltk.cached_property
    def year(self):
        return self.raw_object['year']
        # return self.raw_object.get('year', '')


ds_imdb = rltk.Dataset(rltk.CSVReader('../movies2/csv_files/imdb_clean.csv'), record_class=IMDBRecord,
                       adapter=rltk.MemoryKeyValueAdapter())


# print(ds_imdb.generate_dataframe().head(10))
# for r_imdb in ds_imdb.head(5):
#     print(r_imdb.id, r_imdb.name_string, r_imdb.name_tokens, r_imdb.year)

# %%
@rltk.remove_raw_object
class TMDRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = "tmd"

    @rltk.cached_property
    def id(self):
        return self.raw_object['ID']

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['title']
        # return self.raw_object.get('name', '')

    @rltk.cached_property
    def name_tokens(self):
        return set(tokenizer.tokenize(self.name_string))

    @rltk.cached_property
    def year(self):
        return self.raw_object['year']


ds_tmd = rltk.Dataset(rltk.CSVReader('../movies2/csv_files/tmd.csv'), record_class=TMDRecord,
                      adapter=rltk.MemoryKeyValueAdapter())

# for r_tmd in ds_tmd.head(20):
#     print(r_tmd.id, r_tmd.name_string, r_tmd.name_tokens, r_tmd.year)

# %%
# Blocking
bg = rltk.HashBlockGenerator()
block = bg.generate(
    bg.block(ds_imdb, property_='year'),
    bg.block(ds_tmd, property_='year')
)


# for idx, b in enumerate(block.key_set_adapter):
#     if idx == 5:
#         break
#     print(b)

# %%
# Pairwise comparison
def is_pair(r1, r2):
    for n1, n2 in zip(sorted(r1.name_string), sorted(r2.name_string)):
        if rltk.levenshtein_distance(n1, n2) > min(len(n1), len(n2)) / 3:
            return False
    return True


# Load ltable.ID, rtable.ID and class_label from labeled_data.csv
label_class = {}
line_num = 1
correct_labeled_pair = 0
with open('../movies2/csv_files/labeled_data.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if line_num >= 7:
            label_class[(int(row[1]), int(row[2]))] = row[-1]
            if row[-1] == '1':
                correct_labeled_pair += 1
        line_num += 1
# print(label_class)

# %%
# TODO: Is that ok to just hard-code all pair numbers?
all_pair_num = 99178317
blocked_pair_num = 0
correct_blocked_pair = 0
correct_blocked_labeled_pair = 0
with open('../Xirui_Zhong_hw03_blocked.csv', 'w', newline='') as file:
    for r_imdb, r_tmd, in rltk.get_record_pairs(ds_imdb, ds_tmd, block=block):
        # Output blocked data to a csv file with no header
        writer = csv.writer(file)
        writer.writerow((r_imdb.id, r_tmd.id))
        blocked_pair_num += 1  # pairs in the blocking

        if is_pair(r_imdb, r_tmd):
            correct_blocked_pair += 1
            ltable_id = r_imdb.id; rtable_id = r_tmd.id
            key = (int(ltable_id), int(rtable_id))
            if key in label_class and label_class[key] == '1':
                correct_blocked_labeled_pair += 1
            # print(r_imdb.name_string, r_tmd.name_string)

# TODO: is Reduction ratio correct?
print('Reduction ratio is:')
print(1 - blocked_pair_num / all_pair_num)
print('pairs completeness is:')
print(correct_blocked_labeled_pair / correct_labeled_pair)

# Reduction ratio is:
# 0.9642440595155491
# pairs completeness is:
# 0.9375

#%%
