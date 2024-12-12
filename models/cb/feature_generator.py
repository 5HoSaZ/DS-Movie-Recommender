import torch
import torch.nn as nn


class FeatureGenerator(nn.Module):
    def __init__(self, tf_matrix: torch.Tensor):
        super(FeatureGenerator, self).__init__()
        self.num_feature = tf_matrix.shape[1]
        self.tf_matrix = tf_matrix

    def to(self, device):
        self.tf_matrix = self.tf_matrix.to(device)
        return super().to(device)

    def __call__(self, items):
        features = self.tf_matrix[items]
        return features
