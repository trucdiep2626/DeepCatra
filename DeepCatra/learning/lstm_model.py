import torch
import torch.nn as nn
from lstm_preprocess import encoding

opcode_dict = encoding()


class LSTM_net(nn.Module):
    def __init__(self):
        super(LSTM_net, self).__init__()

        # Input: [batch_size, sequence_len] chứa ID của opcode (được mã hóa).
        # Output: [batch_size, sequence_len, 128] – nhúng thành vector 128 chiều.
        self.embedding = nn.Embedding(len(opcode_dict), 128)

        # input_size=128: đầu vào là vector nhúng từ Embedding.
        # hidden_size=256: mỗi hướng có 256 đơn vị ẩn → tổng 512 đầu ra vì bidirectional.
        # num_layers=2: hai lớp LSTM chồng nhau.
        # dropout=0.3: chống overfitting giữa các lớp.
        # bidirectional=True: LSTM hai chiều, đọc chuỗi từ trái và phải.
        # batch_first=True: input có shape [batch_size, seq_len, input_size].
        self.lstm = nn.LSTM(
            input_size=128,
            hidden_size=256,
            num_layers=2,
            dropout=0.3,
            bidirectional=True,
            batch_first=True,
        )
        # nén xuống 64 -> 32 chiều.
        self.fc1 = nn.Sequential(nn.Linear(512, 64), nn.Tanh())
        self.fc2 = nn.Sequential(nn.Linear(64, 32), nn.Tanh())
        # hàm kích hoạt
        self.tanh = nn.Tanh()

    def forward(self, x):
        # luồng xử lý dữ liệu đầu vào
        # if x.size(1) == 0:  # sequence length = 0
        #     print(x.shape)
        #     raise ValueError(
        #         "⛔️ Lỗi: Input sequence length = 0. Hãy kiểm tra dữ liệu đầu vào."
        #     )
        x = self.embedding(x)  # [B, T] → [B, T, D], nhúng token (opcode) thành vector
        if x.dim() == 2:
            x = x.unsqueeze(0)
        x, _ = self.lstm(x)  # [B, T, D] → [B, T, H], LSTM xử lý chuỗi vector
        x = self.fc1(x[:, -1, :])  # Lấy hidden state cuối cùng → [B, H] → [B, H']
        x = self.fc2(x)  # [B, H'] → [B, C] (số lớp/mục tiêu đầu ra)
        x = self.tanh(
            torch.mean(x, 0)
        )  # Trung bình theo batch → [C], rồi kích hoạt tanh
        return x
