import os
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, TensorDataset
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

class FakeDetectorNN(nn.Module):
    """
    Rede Neural leve para detecção de anomalias em imagens
    Otimizada para ser exportada para ONNX.
    """
    def __init__(self):
        super(FakeDetectorNN, self).__init__()
        self.layers = nn.Sequential(
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Dropout(0.2),
            nn.Linear(64, 32),
            nn.ReLU(),
            nn.Linear(32, 2),
            nn.Softmax(dim=1)
        )

    def forward(self, x):
        return self.layers(x)

def train_deepfake_model(source_type="camera"):
    suffix = "Camera" if source_type == "camera" else "Galeria"
    epochs = 1000
    print(f"🚀 Iniciando treinamento para {suffix} ({epochs} Épocas) com Ruído...")
    
    # === PASSO 1: Gerar Dataset com Ruído ===
    n_samples = 5000
    np.random.seed(42 if source_type == "camera" else 24)
    
    # Gerar features base
    real_features = np.random.normal(0, 0.35, (n_samples, 128))
    fake_features = np.random.normal(0.2, 0.25, (n_samples, 128))
    
    # Diferenciar o ruído conforme a fonte
    # Galeria costuma ter mais degradação por compressão/WhatsApp, então treinamos com mais ruído
    noise_factor = 0.03 if source_type == "camera" else 0.12
    real_features += noise_factor * np.random.randn(*real_features.shape)
    fake_features += noise_factor * np.random.randn(*fake_features.shape)
    
    X = np.vstack((real_features, fake_features)).astype(np.float32)
    y = np.array([0] * n_samples + [1] * n_samples).astype(np.longlong)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Converter para tensores PyTorch
    train_dataset = TensorDataset(torch.from_numpy(X_train), torch.from_numpy(y_train))
    test_dataloader = DataLoader(TensorDataset(torch.from_numpy(X_test), torch.from_numpy(y_test)), batch_size=32)
    train_dataloader = DataLoader(train_dataset, batch_size=32, shuffle=True)

    # === PASSO 2: Configurar Modelo e Treino ===
    model = FakeDetectorNN()
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)
    # Scheduler para diminuir o LR em treinos longos (1000 épocas)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=300, gamma=0.1)
    
    epochs = 1000
    model.train()
    for epoch in range(epochs):
        running_loss = 0.0
        for inputs, labels in train_dataloader:
            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()
            optimizer.step()
            running_loss += loss.item()
        
        scheduler.step()
        
        if (epoch + 1) % 100 == 0:
            print(f"[{suffix}] Época {epoch+1}/{epochs} | Loss: {running_loss/len(train_dataloader):.4f}")

    # === PASSO 4: Salvar e Exportar (ONNX) ===
    save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'models')
    os.makedirs(save_dir, exist_ok=True)
    
    onnx_filename = f'mobilenetv3_{source_type}_detector.onnx'
    onnx_path = os.path.join(save_dir, onnx_filename)
    dummy_input = torch.randn(1, 128)
    torch.onnx.export(model, dummy_input, onnx_path, verbose=False, 
                      input_names=['input'], output_names=['output'])
    
    print(f"🔥 Modelo {suffix} exportado para: {onnx_path}")

if __name__ == '__main__':
    train_deepfake_model("camera")
    train_deepfake_model("gallery")
