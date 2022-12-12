import torch


# softmax function to convert logit to multi-class probabilities
def softmax(logit):
    z = torch.exp(logit)
    return z/z.sum(axis=1).unsqueeze(1)

# convert class probabilities to class labels
def to_classlabel(z):
    row_max = z.max(axis=1).values.unsqueeze(1)
    one_hot = (z == row_max).to(torch.int8)
    one_hot_class = one_hot*torch.tensor(range(0,one_hot.shape[1])).unsqueeze(0)
    return one_hot_class.sum(axis=1)

# classification accuracy
def accuracy(y_pred, y_true):
  acc = (y_pred == y_true).sum()/y_true.numel()
  return acc


# model training
def train(model, loader, loss_func, optimizer, device):
    model.train()
    epoch_loss = 0.0
    epoch_acc = 0.0

    for batch_idx, (features, labels, img_path) in enumerate(loader):

        features = features.to(device)
        labels = labels.to(device)

        logits = model(features)

        sm = softmax(logits)

        y_pred = to_classlabel(sm)

        loss = loss_func(logits, labels)

        acc = accuracy(y_pred, labels)

        optimizer.zero_grad()

        loss.backward()

        optimizer.step()

        epoch_loss += loss.item()
        epoch_acc += acc

        print(f"      Batch: {batch_idx + 1} | Loss: {loss: .4f} | Acc.: {100 * acc: .2f} %")

    return epoch_loss / len(loader), epoch_acc / len(loader)


# model evaluation
def evaluate(model, loader, loss_func, device):
    model.eval()
    epoch_loss = 0.0
    epoch_acc = 0.0

    with torch.no_grad():
        for batch_idx, (features, labels, img_path) in enumerate(loader):
            features = features.to(device)
            labels = labels.to(device)

            logits = model(features)

            sm = softmax(logits)

            y_pred = to_classlabel(sm)

            loss = loss_func(logits, labels)

            acc = accuracy(y_pred, labels)

            epoch_loss += loss.item()
            epoch_acc += acc

        return epoch_loss / len(loader), epoch_acc / len(loader)



def model_training(NUM_EPOCHS, TRAIN_LOADER, VALID_LOADER, MODEL, CRITERION, OPTIMIZER, DEVICE, MODEL_OUTPUT_URL):
    # create tensors to store accuracy and loss values for each epoch
    acc_trend = torch.empty(size=(NUM_EPOCHS, 2))
    loss_trend = torch.empty(size=(NUM_EPOCHS, 2))
    best_valid_acc = 0.0

    for epoch in range(NUM_EPOCHS):

        print(f"EPOCH {epoch + 1}:")

        # train the model and return epoch loss and accuracy
        train_loss, train_acc = train(MODEL, TRAIN_LOADER, CRITERION, OPTIMIZER, DEVICE)

        # validate the model and return epoch loss and accuracy
        valid_loss, valid_acc = evaluate(MODEL, VALID_LOADER, CRITERION, DEVICE)

        # store accuracy and loss values
        acc_trend[epoch] = torch.tensor([train_acc, valid_acc])
        loss_trend[epoch] = torch.tensor([train_loss, valid_loss])

        if valid_acc > best_valid_acc:
            best_valid_acc = valid_acc
            torch.save(MODEL, MODEL_OUTPUT_URL)

        print(f"train loss: {train_loss: .4f} | train acc.: {100 * train_acc: .2f} %")
        print(f"valid loss: {valid_loss: .4f} | valid acc.: {100 * valid_acc: .2f} %")
        print("-------------------------------------------------------------------")

    return acc_trend, loss_trend