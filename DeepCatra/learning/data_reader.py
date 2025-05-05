import os
import numpy as np
from lstm_preprocess import encoding, split_opcode_seq


# "/Users/trucdiep/DeepCatra/Dataset/train_dataset/benign_train/20ADE1A8790AF9C2D0BDC5D1588EA8359DD58C09B3B0300AC8B8D5683B52C14F/sensitive_opcode_seq.txt"
# "/Users/trucdiep/DeepCatra/Dataset/train_dataset/benign_train/57621CA162A69A4A2BCE62B5A23352EAB5A8112875181329D8D6660246B1B8FD/sensitive_opcode_seq.txt"
def load_my_data_split(deal_folder, split_length):

    opcode_dict = encoding()
    feature_data = []
    with open(deal_folder, "r", encoding="utf-8") as file:

        opcode_seq = []
        for line in file.readlines():
            line = line.strip("\n")
            if line == "" and len(opcode_seq) != 0:
                feature_data.extend(opcode_seq)
                opcode_seq = []
            elif line.find(":") == -1 and line != "":
                opcode_seq.append(np.int32(opcode_dict[line]))
        if len(opcode_seq) != 0:
            if len(opcode_seq) >= split_length:
                feature_data.extend(split_opcode_seq(opcode_seq, split_length))
    return feature_data


def get_data(path, ln, split_length):

    # path_benign = os.path.join(path, "benign")
    # path_malicious = os.path.join(path, "malware")
    # hash_list = os.listdir(path_malicious) + os.listdir(path_benign)
    dir = os.listdir(path)

    graph_vertix = []
    graph_edge = []
    lstm_feature = []
    labels = []

    i = -1
    for files in dir:  # 遍历文件夹
        sub_path = os.path.join(path, files)
        file = os.listdir(sub_path)
        i = i + 1
        print(files)
        for apk in file:
            sub_sub_path = os.path.join(sub_path, apk)
            edge_path = os.path.join(sub_sub_path, "edge.txt")
            vertix_path = os.path.join(sub_sub_path, "vertix.txt")
            opcode = "sensitive_opcode_seq.txt"
            opcode_path = os.path.join(sub_sub_path, opcode)
            vandeando = os.listdir(sub_sub_path)
            if "malware" in files:
                labels.append(1)
            else:
                labels.append(0)
            for vande in vandeando:
                if vande == "edge.txt":
                    edge_info = open(edge_path)
                    lines = edge_info.readlines()
                    edge = np.zeros((len(lines), 3), dtype=int)
                    j = 0
                    for line in lines:
                        curline = line.strip("\n")
                        curline = curline.split()
                        curline = [int(i) for i in curline]
                        curline = np.array(curline)
                        edge[j] = curline
                        j += 1
                    graph_edge.append(np.array(edge))

                if vande == "vertix.txt":
                    vertix_info = open(vertix_path)
                    i = 0
                    lines = vertix_info.readlines()
                    vertix = np.zeros((len(lines), ln), dtype=float)

                    for line in lines:
                        curline = line.strip("\n")
                        curline = curline.split()
                        curline = [int(i) for i in curline]

                        if len(curline) < ln:
                            curline = list(curline + [0] * (ln - len(curline)))
                        if len(curline) > ln:
                            curline = curline[:ln]
                        curline = np.array(curline)
                        curline = curline.astype(float)

                        # 归一化
                        curline = curline / 232
                        vertix[i] = curline
                        i += 1
                    graph_vertix.append(vertix)

                if vande == opcode:

                    single_apk_data = load_my_data_split(opcode_path, split_length)
                    single_apk_data = np.array(single_apk_data)
                    if single_apk_data.size == 0:
                        print(opcode_path)
                    lstm_feature.append(np.array(single_apk_data))
    num1 = 0
    num0 = 0
    print(len(graph_edge))
    print(len(graph_vertix))
    print(len(labels))
    print(len(lstm_feature))
    for x in labels:
        if x == 1:
            num1 += 1
        if x == 0:
            num0 += 1
    print(num1)
    print(num0)
    # count_label_distribution(lstm_feature, labels)
    return labels, graph_vertix, graph_edge, lstm_feature


# def count_label_distribution(lstm_feature, labels):
#     malware_count = 0
#     benign_count = 0
#     for feat, label in zip(lstm_feature, labels):
#         if len(feat) == 0:
#             if label == 1:  # giả sử 1 = malware
#                 malware_count += 1
#             else:
#                 benign_count += 1
#     print(f"🛑 Rỗng: malware = {malware_count}, benign = {benign_count}")


# import os
# import shutil

# # Define root and target directories
# root_dir = "/Users/trucdiep/DeepCatra/Dataset/DeepCatra_Features"
# malware_dir = "/Users/trucdiep/DeepCatra/Dataset/malware"
# benign_dir = "/Users/trucdiep/DeepCatra/Dataset/benign"


# def count_subfolders(path):
#     return sum(os.path.isdir(os.path.join(path, name)) for name in os.listdir(path))


# malware_count = count_subfolders(malware_dir)
# benign_count = count_subfolders(benign_dir)

# print(f"Malware folders: {malware_count}")
# print(f"Benign folders: {benign_count}")


# # Lấy tên subfolder trong mỗi thư mục
# benign_subfolders = set(os.listdir(benign_dir)) if os.path.exists(benign_dir) else set()
# malware_subfolders = (
#     set(os.listdir(malware_dir)) if os.path.exists(malware_dir) else set()
# )

# # Tìm các tên trùng nhau
# duplicate_names = benign_subfolders.intersection(malware_subfolders)

# # Kết quả
# if duplicate_names:
#     print(f"🔁 Có {len(duplicate_names)} thư mục trùng tên trong benign và malware:")
#     for name in sorted(duplicate_names):
#         print(f" - {name}")
# else:
#     print("✅ Không có thư mục nào trùng tên giữa benign và malware.")


# import os
# import shutil

# # Thư mục chứa các subfolder gốc
# source_dir = "/Users/trucdiep/DeepCatra/Dataset/DeepCatra_Features/"

# # Duyệt qua các file .txt
# for txt_file in os.listdir("/Users/trucdiep/DeepCatra/Dataset/"):
#     if txt_file.endswith(".txt"):
#         folder_name = txt_file.replace(".txt", "")
#         target_dir = os.path.join("/Users/trucdiep/DeepCatra/Dataset/", folder_name)
#         os.makedirs(target_dir, exist_ok=True)

#         print(f"\n📂 Đang xử lý file: {txt_file}")
#         with open("/Users/trucdiep/DeepCatra/Dataset/" + txt_file, "r") as f:
#             for line in f:
#                 subfolder = line.strip()
#                 src = os.path.join(source_dir, subfolder)
#                 dst = os.path.join(target_dir, subfolder)
#                 if os.path.isdir(src):
#                     shutil.copytree(src, dst)
#                     print(f"✅ Moved: {subfolder} → {folder_name}")
#                 else:
#                     print(f"⚠️ Không tìm thấy thư mục: {subfolder}")


# import os

# dataset_root = "Dataset"  # thư mục gốc

# # Lặp qua các thư mục con trong Dataset
# for subfolder in os.listdir(dataset_root):
#     full_path = os.path.join(dataset_root, subfolder)
#     if os.path.isdir(full_path):
#         # Đếm số thư mục con (chỉ tính folder, không tính file)
#         subdirs = [
#             d
#             for d in os.listdir(full_path)
#             if os.path.isdir(os.path.join(full_path, d))
#         ]
#         print(f"{subfolder}: {len(subdirs)} subfolder(s)")


# import os


# def check_empty_opcode_seq(dataset_root):
#     empty_apps = []
#     total_apps = 0

#     for app_folder in sorted(os.listdir(dataset_root)):
#         app_path = os.path.join(dataset_root, app_folder)
#         if not os.path.isdir(app_path):
#             continue

#         total_apps += 1
#         opcode_file = os.path.join(app_path, "sensitive_opcode_seq.txt")

#         if not os.path.exists(opcode_file):
#             print(f"❌ File không tồn tại: {opcode_file}")
#             empty_apps.append((app_folder, "missing"))
#             continue

#         if os.path.getsize(opcode_file) == 0:
#             print(f"⚠️ File rỗng: {opcode_file}")
#             empty_apps.append((app_folder, "empty"))

#     print("\n📋 Tổng số ứng dụng kiểm tra:", total_apps)
#     print("🚫 Số ứng dụng có file opcode rỗng hoặc thiếu:", len(empty_apps))

#     # Ghi vào file log
#     with open("empty_sensitive_opcode_apps.txt", "w") as f:
#         for app_name, reason in empty_apps:
#             f.write(f"{app_name} ({reason})\n")

#     print("✅ Danh sách ứng dụng lỗi đã ghi vào 'empty_sensitive_opcode_apps.txt'.")


# # Gọi hàm với thư mục tập train/test
# check_empty_opcode_seq("/Users/trucdiep/DeepCatra/Dataset/train_dataset/benign_train")
# check_empty_opcode_seq("/Users/trucdiep/DeepCatra/Dataset/train_dataset/malware_train")


# import os
# import shutil
# import random


# def move_half_subfolders(source_dir, target_dir):
#     if not os.path.exists(source_dir):
#         print(f"Source directory does not exist: {source_dir}")
#         return
#     if not os.path.exists(target_dir):
#         os.makedirs(target_dir)

#     # List only subdirectories
#     subfolders = [
#         f for f in os.listdir(source_dir) if os.path.isdir(os.path.join(source_dir, f))
#     ]

#     # Shuffle and take half
#     random.shuffle(subfolders)
#     half_count = 65
#     folders_to_move = subfolders[:half_count]

#     # Move each folder
#     for folder in folders_to_move:
#         src_path = os.path.join(source_dir, folder)
#         dst_path = os.path.join(target_dir, folder)
#         print(f"Moving: {src_path} -> {dst_path}")
#         shutil.copytree(src_path, dst_path)

#     print(f"\nMoved {half_count} subfolders from {source_dir} to {target_dir}.")


# # Example usage:
# source = "/Users/trucdiep/DeepCatra/Dataset/valid_dataset/benign_valid"
# target = "/Users/trucdiep/DeepCatra/Dataset/valid_dataset3/benign_valid"
# # source = "/Users/trucdiep/DeepCatra/Dataset/train_dataset/malware_train"
# # target = "/Users/trucdiep/DeepCatra/Dataset/train_dataset3/malware_train"
# move_half_subfolders(source, target)
