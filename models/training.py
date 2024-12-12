import torch
import torch.nn as nn
from torch.optim import Optimizer
from torch.utils.data import DataLoader

from typing import Literal


def train_model(
    epoch: int,
    model: nn.Module,
    dataloader: DataLoader,
    loss_fn: nn.Module,
    optimizer: Optimizer,
    device: Literal["cpu", "cuda"],
):
    model.train()
    train_loss = 0
    train_mae = 0
    batch = 0
    for user, item, rating in dataloader:
        user, item = user.to(device), item.to(device)
        rating = rating.unsqueeze(1).to(device)
        optimizer.zero_grad()
        # Get predition
        pred = model(user, item)
        # Calculate loss and mae
        loss = loss_fn(pred, rating)
        mae = nn.L1Loss()(pred, rating)
        # Update parameters
        loss.backward()
        optimizer.step()
        # Update metrics
        train_loss += loss.item()
        train_mae += mae.item()
        batch += 1
        print(f"Epoch {epoch} --- Training: Batch {batch}/{len(dataloader)}", end="\r")
    train_loss /= len(dataloader)
    train_mae /= len(dataloader)
    return train_loss, train_mae


def test_model(
    epoch: int,
    model: nn.Module,
    dataloader: DataLoader,
    loss_fn: nn.Module,
    device: Literal["cpu", "cuda"],
):
    model.eval()
    test_loss = 0
    test_mae = 0
    batch = 0
    with torch.no_grad():
        for user, item, rating in dataloader:
            user, item = user.to(device), item.to(device)
            rating = rating.unsqueeze(1).to(device)
            # Get predition
            pred = model(user, item)
            # Calculate loss and mae
            loss = loss_fn(pred, rating)
            mae = nn.L1Loss()(pred, rating)
            # Update metrics
            test_loss += loss.item()
            test_mae += mae.item()
            batch += 1
            print(
                f"Epoch {epoch} --- Test: Batch {batch}/{len(dataloader)}         ",
                end="\r",
            )
    test_loss /= len(dataloader)
    test_mae /= len(dataloader)
    return test_loss, test_mae
