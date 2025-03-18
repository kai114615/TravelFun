# 圖像搜尋功能安裝指南

本文檔提供了在不同作業系統上安裝和設置TravelFun以圖搜貨功能的詳細指南。

## 目錄

1. [環境需求](#環境需求)
2. [macOS安裝指南](#macos安裝指南) (Apple Silicon和Intel)
3. [Windows安裝指南](#windows安裝指南)
4. [Linux安裝指南](#linux安裝指南)
5. [常見問題](#常見問題)

## 環境需求

- Python 3.8或更高版本
- Django 3.2或更高版本
- 足夠的儲存空間用於模型和依賴 (約1-2GB)

## macOS安裝指南

### Apple Silicon (M1/M2/M3系列)處理器

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv #若已建立此行可省略
source funenv/bin/activate
```

2. **安裝依賴**:
```bash
pip install -r requirements.clip.mac.txt
```

3. **設置MPS加速** (可選但推薦):
```bash
export PYTORCH_ENABLE_MPS_FALLBACK=1
```

4. **測試安裝**:
```bash
python -c "import torch; print(f'MPS可用: {torch.backends.mps.is_available()}')"
```

### Intel處理器

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv #若已建立此行可省略
source funenv/bin/activate
```

2. **安裝依賴**:
```bash
pip install -r requirements.clip.txt
pip install torch torchvision torchaudio
pip install faiss-cpu
```

## Windows安裝指南

### 有NVIDIA GPU的Windows系統

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv #若已建立此行可省略
funenv\Scripts\activate
```

2. **安裝依賴**:
```bash
pip install -r requirements.clip.windows.txt
```

3. **測試安裝**:
```bash
python -c "import torch; print(f'CUDA可用: {torch.cuda.is_available()}')"
```

### 無GPU的Windows系統

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv
funenv\Scripts\activate
```

2. **安裝依賴** (CPU版本):
```bash
pip install -r requirements.clip.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install faiss-cpu
```

## Linux安裝指南

### 有NVIDIA GPU的Linux系統

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv #若已建立此行可省略
source funenv/bin/activate
```

2. **安裝CUDA版PyTorch**:
```bash
pip install -r requirements.clip.txt
pip install torch torchvision torchaudio
pip install faiss-gpu
```

### 無GPU的Linux系統

1. **建立並啟用虛擬環境**:
```bash
cd DjangoAdmin2
python -m venv funenv #若已建立此行可省略
source funenv/bin/activate
```

2. **安裝CPU版PyTorch**:
```bash
pip install -r requirements.clip.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
pip install faiss-cpu
```

## 常見問題

### 1. CLIP模型下載失敗

如果CLIP模型下載失敗，可能是由於網絡問題。嘗試以下解決方案:

- 確保網絡連接穩定
- 使用VPN連接 (如有需要)
- 手動下載模型檔案，放置在`~/.cache/clip`目錄中

### 2. CUDA顯示可用但仍使用CPU

檢查CUDA版本是否與PyTorch兼容:

```bash
python -c "import torch; print(f'CUDA版本: {torch.version.cuda}')"
```

確保CUDA驅動程序是最新的。

### 3. MPS加速不工作

在Apple Silicon Mac上，如果MPS加速不工作:

- 更新macOS至最新版本
- 確保環境變數已正確設置
- 嘗試重新安裝PyTorch

### 4. 記憶體錯誤

如果遇到記憶體錯誤:

- 減小批處理大小 (修改`settings.py`中的`MAX_BATCH_SIZE`)
- 確保關閉其他記憶體密集型應用程序
- 考慮使用較小的模型版本 (例如從ViT-B/16降級到ViT-B/32)

### 5. Windows上安裝FAISS遇到問題

FAISS在Windows上安裝可能較複雜。建議嘗試:

- 使用預編譯的wheel文件進行安裝
- 嘗試使用conda安裝: `conda install -c conda-forge faiss-cpu`

## 貢獻者

如遇到其他安裝問題，請聯繫開發團隊。 