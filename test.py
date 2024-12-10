from models.cf import EmbededDotNet
import torch

net = EmbededDotNet(2, 2)
net.eval()

users = torch.tensor([[1, 0], [1, 0]], dtype=torch.int64)
items = torch.tensor([[0, 1], [1, 0]], dtype=torch.int64)

out = net(users, items)
print(out)
