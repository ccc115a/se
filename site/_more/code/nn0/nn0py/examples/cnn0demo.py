# mnist.py
import os
import gzip
import urllib.request
import random

from nn0 import Value, Adam, cross_entropy
from cnn0 import CNN

# 在 mnist.py 中修改
def load_mnist_data():
    base_url = "https://storage.googleapis.com/cvdf-datasets/mnist/"
    files = {
        "train_img": "_data/train-images-idx3-ubyte.gz",  # 加上 data/
        "train_lbl": "_data/train-labels-idx1-ubyte.gz",
        "test_img": "_data/t10k-images-idx3-ubyte.gz",
        "test_lbl": "_data/t10k-labels-idx1-ubyte.gz",
    }

    for name, filename in files.items():
        if not os.path.exists(filename):
            print(f"正在下載 {filename} ...")
            urllib.request.urlretrieve(base_url + filename, filename)
            
    def read_images(filename):
        with gzip.open(filename, 'rb') as f: data = f.read()
        return data[16:] # 略過標頭
        
    def read_labels(filename):
        with gzip.open(filename, 'rb') as f: data = f.read()
        return data[8:]  # 略過標頭
        
    print("載入 MNIST 至記憶體中...")
    return (read_images(files["train_img"]), read_labels(files["train_lbl"]),
            read_images(files["test_img"]),  read_labels(files["test_lbl"]))

def preprocess_image(raw_data, index):
    """
    取出第 index 張 28x28 影像。
    為了加速純 Python 的運算，我們使用 stride=2 降採樣將其轉換為 14x14，
    並將數值縮放至 0~1 後封裝成 Value。
    """
    start = index * 784
    img_28 = raw_data[start:start+784]
    
    img_14 =[]
    for i in range(14):
        row =[]
        for j in range(14):
            # 取樣位置: 2*i 行, 2*j 列
            val = img_28[(2*i)*28 + (2*j)]
            row.append(Value(val / 255.0))
        img_14.append(row)
        
    return [img_14] # 確保回傳形狀為 (1, 14, 14)

def main():
    X_train, y_train, X_test, y_test = load_mnist_data()
    
    # 初始化模型與優化器
    model = CNN()
    # 建立 Adam 優化器
    optimizer = Adam(model.parameters(), lr=0.005)
    
    # 由於純 Python 運算速度瓶頸，這裡我們只訓練少部分的資料作為示範
    num_train = 1000
    num_epochs = 5
    
    print(f"\n--- 開始訓練 (由於純Python引擎較慢，僅訓練 {num_train} 筆樣本，共 {num_epochs} Epochs) ---")
    
    for epoch in range(num_epochs):
        total_loss = 0.0
        correct = 0
        
        # 每個 epoch 打亂順序
        indices = list(range(num_train))
        random.shuffle(indices)
        
        for step, idx in enumerate(indices):
            x = preprocess_image(X_train, idx)
            y = y_train[idx]
            
            # Forward pass
            logits = model(x)
            loss = cross_entropy(logits, y)
            
            # 計算是否正確
            pred = max(range(10), key=lambda i: logits[i].data)
            if pred == y:
                correct += 1
            
            # Backward pass 
            # 反向傳播：計算計算圖中所有 Value 節點的梯度
            loss.backward()
            
            # Update parameters
            # Adam 優化器執行一步並將 p.grad 歸零
            optimizer.step()
            
            total_loss += loss.data
            
            # 顯示進度
            if (step + 1) % 20 == 0:
                print(f"Epoch {epoch+1}, Step {step+1:3d}/{num_train}, Loss: {loss.data:.4f}")
                
        acc = correct / num_train * 100
        avg_loss = total_loss / num_train
        print(f"➔ Epoch {epoch+1} 總結: 平均 Loss: {avg_loss:.4f}, 準確率: {acc:.2f}%\n")
        
    # 測試集驗證
    num_test = 50
    print(f"--- 測試階段 (抽取 {num_test} 筆測試樣本) ---")
    correct = 0
    for idx in range(num_test):
        x = preprocess_image(X_test, idx)
        y = y_test[idx]
        
        logits = model(x)
        pred = max(range(10), key=lambda i: logits[i].data)
        if pred == y:
            correct += 1
            
    print(f"測試準確率: {correct / num_test * 100:.2f}%")

if __name__ == '__main__':
    main()