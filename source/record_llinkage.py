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


class IMDBRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = "IMDB"

    @rltk.cached_property
    def id(self):
        return str(int(self.raw_object['ID']))

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['name']
        # return self.raw_object.get('name', '')

    @rltk.cached_property
    def year(self):
        return self.raw_object['year']
        # return self.raw_object.get('year', '')

    @rltk.cached_property
    def director(self):
        return self.raw_object['director']

    @rltk.cached_property
    def director_tokens(self):
        return set(tokenizer.tokenize(self.director))


ds_imdb = rltk.Dataset(rltk.CSVReader('../movies2/csv_files/imdb_clean.csv'), record_class=IMDBRecord,
                       adapter=rltk.MemoryKeyValueAdapter())


# print(ds_imdb.generate_dataframe().head(10))
# for r_imdb in ds_imdb.head(26):
#     print(r_imdb.id, r_imdb.name_string, r_imdb.year, r_imdb.director, r_imdb.director_tokens)


# %%
@rltk.remove_raw_object
class TMDRecord(rltk.Record):
    def __init__(self, raw_object):
        super().__init__(raw_object)
        self.name = "tmd"

    @rltk.cached_property
    def id(self):
        return str(int(self.raw_object['ID']))

    @rltk.cached_property
    def name_string(self):
        return self.raw_object['title']
        # return self.raw_object.get('name', '')

    # @rltk.cached_property
    # def name_tokens(self):
    #     return set(tokenizer.tokenize(self.name_string))

    @rltk.cached_property
    def year(self):
        return self.raw_object['year']

    @rltk.cached_property
    def director(self):
        return self.raw_object['director(s)']

    @rltk.cached_property
    def director_tokens(self):
        return set(tokenizer.tokenize(self.director))


ds_tmd = rltk.Dataset(rltk.CSVReader('../movies2/csv_files/tmd.csv'), record_class=TMDRecord,
                      adapter=rltk.MemoryKeyValueAdapter())

# for r_tmd in ds_tmd.head(26):
#     print(r_tmd.id, r_tmd.name_string, r_tmd.year, r_tmd.director, r_tmd.director_tokens)


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
# Load ltable.ID, rtable.ID and class_label from labeled_data.csv
label_class = {}
line_num = 1
correct_labeled_pair = 0  # 256
gt = rltk.GroundTruth()  # Generate ground truth
with open('../movies2/csv_files/labeled_data.csv', 'r') as file:
    reader = csv.reader(file)
    for row in reader:
        if line_num >= 7:
            label_class[(int(row[1]), int(row[2]))] = row[-1]
            if row[-1] == '1':
                correct_labeled_pair += 1
                gt.add_positive(str(int(row[1])), str(int(row[2])))
            else:
                gt.add_negative(str(int(row[1])), str(int(row[2])))
        line_num += 1
# print(label_class)

# %%
# Generate Ground Truth
# line_num = 1
# gt = rltk.GroundTruth()
# with open('../movies2/csv_files/labeled_data.csv', 'r') as file:
#     # reader = csv.reader(file)
#     for row in rltk.CSVReader(file):
#         if line_num >= 7:
#             if row['class_label'] == '1':
#                 gt.add_positive(row['ltable.ID'], row['rtable.ID'])
#             else:
#                 gt.add_negative(row['ltable.ID'], row['rtable.ID'])
#         line_num += 1


# %%
all_pair = 99178317
blocked_pair = 0  # 3546214
correct_blocked_pair = 0  # 21762
correct_blocked_labeled_pair = 0  # 240 -> 254 if doesn't include is_pair function
with open('../Xirui_Zhong_hw03_blocked.csv', 'w', newline='') as file:
    for r_imdb, r_tmd, in rltk.get_record_pairs(ds_imdb, ds_tmd, block=block):
        # Output blocked data to a csv file with no header
        writer = csv.writer(file)
        writer.writerow((r_imdb.id, r_tmd.id))
        blocked_pair += 1  # pairs in the blocking

        ltable_id = r_imdb.id
        rtable_id = r_tmd.id
        key = (int(ltable_id), int(rtable_id))
        if key in label_class and label_class[key] == '1':
            correct_blocked_labeled_pair += 1

        # if is_pair(r_imdb, r_tmd):
        #     correct_blocked_pair += 1
        #     ltable_id = r_imdb.id; rtable_id = r_tmd.id
        #     key = (int(ltable_id), int(rtable_id))
        #     if key in label_class and label_class[key] == '1':
        #         correct_blocked_labeled_pair += 1
file.close()

print('Reduction ratio is:')
print(1 - blocked_pair / all_pair)
# Pair completeness is calculated as: |number of matches after blocking| / |number of matches|. So you don't want to
# include non-matched pairs when calculating pair completeness.
print('pairs completeness is:')
print(correct_blocked_labeled_pair / correct_labeled_pair)

# Reduction ratio is:
# 0.9642440595155491
# pairs completeness is:
# 0.9375 -> 0.9928 if doesn't include is_pair function


# %%
# Compare string similarities for names
def is_name_pair(r1, r2):
    for n1, n2 in zip(sorted(r1.name_string), sorted(r2.name_string)):
        if rltk.levenshtein_distance(n1, n2) > min(len(n1), len(n2)) / 3:
            return 0
    return 1


def is_director_pair(r1, r2):
    pass


# Compare string similarities for director names
def is_director_token_pair(r1, r2):
    set1 = r1.director_tokens
    set2 = r2.director_tokens
    if len(set1) == len(set2):
        if set1 == set2:
            return 1
        else:
            return 0
    else:
        return 0


# Scoring function to combine field similarities
def rule_based_method(r_1, r_2):
    THRESHOLD = 1
    score_1 = is_name_pair(r_1, r_2)
    score_2 = is_director_token_pair(r_1, r_2)

    total = 0.7 * score_1 + 0.3 * score_2

    # return two values: boolean if they match or not, float to determine confidence
    return total >= THRESHOLD


# Run record linkage method on blocked data
labeled_pred = []
with open('../Xirui_Zhong_hw03_el.csv', 'w', newline='') as file:
    for r_imdb, r_tmd, in rltk.get_record_pairs(ds_imdb, ds_tmd, block=block):
        ltable_id = r_imdb.id
        rtable_id = r_tmd.id
        # Output blocked data to a csv file with no header
        writer = csv.writer(file)
        key = (int(ltable_id), int(rtable_id))
        if rule_based_method(r_imdb, r_tmd):
            writer.writerow((ltable_id, rtable_id, '1'))
            if key in label_class:
                labeled_pred.append((ltable_id, rtable_id, '1'))
        else:
            writer.writerow((ltable_id, rtable_id, '0'))
            if key in label_class:
                labeled_pred.append((ltable_id, rtable_id, '0'))
file.close()


# %%
# Run record linkage method on the pairs in the Labeled Data L
# Evaluate my method on the Labeled Data L using RLTK
trial = rltk.Trial(gt)
with open('../Xirui_Zhong_hw03_el_labeled.csv', 'w', newline='') as file:
    for r_imdb, r_tmd, in rltk.get_record_pairs(ds_imdb, ds_tmd):
        ltable_id = r_imdb.id
        rtable_id = r_tmd.id
        writer = csv.writer(file)
        key = (int(ltable_id), int(rtable_id))
        if key in label_class:
            if rule_based_method(r_imdb, r_tmd):
                writer.writerow((ltable_id, rtable_id, '1'))
                trial.add_positive(r_imdb, r_tmd)
            else:
                writer.writerow((ltable_id, rtable_id, '0'))
                trial.add_negative(r_imdb, r_tmd)
file.close()
trial.evaluate()
print('precison:', trial.precision, 'recall:', trial.recall, 'f-measure:', trial.f_measure)
print('tp:', len(trial.true_positives_list))
print('fp:', len(trial.false_positives_list))
print('tn:', len(trial.true_negatives_list))
print('fn:', len(trial.false_negatives_list))

# precison: 1.0 recall: 0.92578125 f-measure: 0.9614604462474645
# tp: 237
# fp: 0
# tn: 144
# fn: 19


# %%




