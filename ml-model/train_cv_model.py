import os
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms, models
from PIL import Image
from sklearn.model_selection import train_test_split
import numpy as np

# -------------------------
# Enhanced Dataset with PROPER normalization
# -------------------------
class EnhancedFabricDataset(Dataset):
    def __init__(self, annotations_file, transform=None, is_training=False):
        with open(annotations_file, "r") as f:
            self.data = json.load(f)
        self.transform = transform
        self.is_training = is_training
        
        # Calculate normalization stats for semantic features
        self.semantic_means = None
        self.semantic_stds = None
        if is_training:
            self._calculate_normalization_stats()

    def _calculate_normalization_stats(self):
        """Calculate mean and std for semantic features"""
        all_semantic = []
        for item in self.data:
            semantic = [
                item["semantic"]["area_used"],
                item["semantic"]["utilization"],
                item["semantic"]["complexity"],
                item["semantic"]["aspect_ratio"]
            ]
            all_semantic.append(semantic)
        
        all_semantic = np.array(all_semantic)
        self.semantic_means = all_semantic.mean(axis=0)
        self.semantic_stds = all_semantic.std(axis=0)
        
        print(f"Semantic means: {self.semantic_means}")
        print(f"Semantic stds: {self.semantic_stds}")

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        item = self.data[idx]
        
        # Handle file path issues
        file_path = item["file_name"]
        if not os.path.exists(file_path):
            base_name = os.path.basename(file_path)
            possible_paths = [
                file_path,
                f"fabric_dataset_enhanced/train/images/{base_name}",
                f"fabric_dataset_enhanced/val/images/{base_name}", 
                f"fabric_dataset_enhanced/test/images/{base_name}",
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    file_path = path
                    break
            else:
                image = Image.new("RGB", (224, 224), color="gray")
                if self.transform:
                    image = self.transform(image)
                return self._create_dummy_item(image)
        
        try:
            image = Image.open(file_path).convert("RGB")
        except:
            image = Image.new("RGB", (224, 224), color="gray")
        
        if self.transform:
            image = self.transform(image)
            
        # Convert part and defect to indices
        part_idx = self.part_to_idx.get(item["part"], 0)
        defect_idx = self.defect_to_idx.get(item["defect_type"], 0)
        
        # NORMALIZE semantic features
        semantic_features = np.array([
            item["semantic"]["area_used"],
            item["semantic"]["utilization"], 
            item["semantic"]["complexity"],
            item["semantic"]["aspect_ratio"]
        ])
        
        if self.semantic_means is not None:
            semantic_features = (semantic_features - self.semantic_means) / (self.semantic_stds + 1e-8)
            
        return {
            "image": image,
            "part": part_idx,
            "defect": defect_idx,
            "semantic": torch.tensor(semantic_features, dtype=torch.float),
        }
    
    def _create_dummy_item(self, image):
        return {
            "image": image,
            "part": 0,
            "defect": 0,
            "semantic": torch.tensor([0.0, 0.0, 0.0, 0.0], dtype=torch.float),
        }

# -------------------------
# SIMPLIFIED Model Architecture
# -------------------------
class SimpleMultiHeadNet(nn.Module):
    def __init__(self, num_parts, num_defects, semantic_dim):
        super().__init__()
        # Use pre-trained ResNet50
        base = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
        
        self.backbone = nn.Sequential(*list(base.children())[:-1])
        feat_dim = base.fc.in_features
        
        # SIMPLIFIED heads - remove complex layers
        self.part_head = nn.Linear(feat_dim, num_parts)
        self.defect_head = nn.Linear(feat_dim, num_defects)
        self.semantic_head = nn.Linear(feat_dim, semantic_dim)

    def forward(self, x):
        x = self.backbone(x)
        x = torch.flatten(x, 1)
        return self.part_head(x), self.defect_head(x), self.semantic_head(x)

# -------------------------
# Training with PROPER loss scaling
# -------------------------
class EarlyStopping:
    def __init__(self, patience=5, min_delta=0):
        self.patience = patience
        self.min_delta = min_delta
        self.counter = 0
        self.best_loss = None
        self.early_stop = False

    def __call__(self, val_loss):
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss > self.best_loss - self.min_delta:
            self.counter += 1
            if self.counter >= self.patience:
                self.early_stop = True
        else:
            self.best_loss = val_loss
            self.counter = 0

def train_model_fixed():
    annotations = "fabric_dataset_enhanced/annotations.json"
    
    # Load data
    with open(annotations, "r") as f:
        data = json.load(f)

    parts = sorted(set(item["part"] for item in data))
    defects = sorted(set(item["defect_type"] for item in data))
    semantic_dim = 4

    part_to_idx = {p: i for i, p in enumerate(parts)}
    defect_to_idx = {d: i for i, d in enumerate(defects)}

    for item in data:
        item["part"] = part_to_idx[item["part"]]
        item["defect_type"] = defect_to_idx[item["defect_type"]]

    # Create splits
    os.makedirs("fabric_dataset_enhanced/splits", exist_ok=True)
    train_split_path = "fabric_dataset_enhanced/splits/train.json"
    val_split_path = "fabric_dataset_enhanced/splits/val.json"
    
    if not os.path.exists(train_split_path):
        train_data, val_data = train_test_split(data, test_size=0.2, random_state=42)
        with open(train_split_path, "w") as f:
            json.dump(train_data, f)
        with open(val_split_path, "w") as f:
            json.dump(val_data, f)
    else:
        with open(train_split_path, "r") as f:
            train_data = json.load(f)
        with open(val_split_path, "r") as f:
            val_data = json.load(f)

    # Transforms
    train_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    val_transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
    ])

    # Create datasets
    train_dataset = EnhancedFabricDataset(train_split_path, train_transform, is_training=True)
    val_dataset = EnhancedFabricDataset(val_split_path, val_transform, is_training=False)
    
    # Set mappings
    train_dataset.part_to_idx = part_to_idx
    train_dataset.defect_to_idx = defect_to_idx
    val_dataset.part_to_idx = part_to_idx
    val_dataset.defect_to_idx = defect_to_idx

    # Use normalization stats from training set for validation set
    val_dataset.semantic_means = train_dataset.semantic_means
    val_dataset.semantic_stds = train_dataset.semantic_stds

    train_loader = DataLoader(train_dataset, batch_size=32, shuffle=True, num_workers=0)
    val_loader = DataLoader(val_dataset, batch_size=32, num_workers=0)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🚀 Using device: {device}")
    
    model = SimpleMultiHeadNet(len(parts), len(defects), semantic_dim).to(device)

    # Loss functions with PROPER scaling
    criterion_part = nn.CrossEntropyLoss()
    criterion_defect = nn.CrossEntropyLoss()
    criterion_semantic = nn.MSELoss()
    
    # Lower learning rate
    optimizer = optim.Adam(model.parameters(), lr=1e-5, weight_decay=1e-4)
    
    # Gradient clipping to prevent explosions
    early_stopping = EarlyStopping(patience=5)

    best_val_loss = float('inf')
    
    print("Starting training with FIXED normalization...")
    
    for epoch in range(30):
        # Training
        model.train()
        train_loss = 0
        train_part_loss = 0
        train_defect_loss = 0
        train_semantic_loss = 0
        
        for batch in train_loader:
            images = batch["image"].to(device)
            part_labels = batch["part"].to(device)
            defect_labels = batch["defect"].to(device)
            semantic_labels = batch["semantic"].to(device)

            optimizer.zero_grad()
            part_out, defect_out, semantic_out = model(images)
            
            # Calculate individual losses
            part_loss = criterion_part(part_out, part_labels)
            defect_loss = criterion_defect(defect_out, defect_labels)
            semantic_loss = criterion_semantic(semantic_out, semantic_labels)
            
            # Balanced loss weights
            loss = part_loss + defect_loss + (semantic_loss * 0.1)  # Reduce semantic weight
            
            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)
            
            loss.backward()
            optimizer.step()
            
            train_loss += loss.item()
            train_part_loss += part_loss.item()
            train_defect_loss += defect_loss.item()
            train_semantic_loss += semantic_loss.item()

        # Validation
        model.eval()
        val_loss = 0
        with torch.no_grad():
            for batch in val_loader:
                images = batch["image"].to(device)
                part_labels = batch["part"].to(device)
                defect_labels = batch["defect"].to(device)
                semantic_labels = batch["semantic"].to(device)

                part_out, defect_out, semantic_out = model(images)
                
                part_loss = criterion_part(part_out, part_labels)
                defect_loss = criterion_defect(defect_out, defect_labels)
                semantic_loss = criterion_semantic(semantic_out, semantic_labels)
                
                loss = part_loss + defect_loss + (semantic_loss * 0.1)
                val_loss += loss.item()

        train_loss /= len(train_loader)
        val_loss /= len(val_loader)
        
        early_stopping(val_loss)
        
        print(f"Epoch {epoch+1:02d}:")
        print(f"  Train Loss: {train_loss:.4f} (Part: {train_part_loss/len(train_loader):.4f}, "
              f"Defect: {train_defect_loss/len(train_loader):.4f}, Semantic: {train_semantic_loss/len(train_loader):.4f})")
        print(f"  Val Loss: {val_loss:.4f}")
        
        # Save best model - FIXED FOR PYTHON 2.6+ COMPATIBILITY
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            
            # Convert numpy arrays to tensors for safe serialization
            semantic_means_tensor = torch.tensor(train_dataset.semantic_means) if train_dataset.semantic_means is not None else None
            semantic_stds_tensor = torch.tensor(train_dataset.semantic_stds) if train_dataset.semantic_stds is not None else None
            
            # Save in PyTorch 2.6+ compatible format
            torch.save({
                "model_state_dict": model.state_dict(),
                "part_to_idx": part_to_idx,
                "defect_to_idx": defect_to_idx,
                "semantic_dim": semantic_dim,
                "semantic_means": semantic_means_tensor,  # Converted to tensor
                "semantic_stds": semantic_stds_tensor,    # Converted to tensor
                "val_loss": val_loss,
                "epoch": epoch,
                "model_architecture": "SimpleMultiHeadNet",
                "model_class": "SimpleMultiHeadNet",
                "base_model": "resnet50",
                "num_parts": len(parts),
                "num_defects": len(defects),
            }, "fixed_multihead_fabric_model_safe.pth", _use_new_zipfile_serialization=True)
            
            print(f"  💾 New best model saved with val_loss: {val_loss:.4f}")
        
        if early_stopping.early_stop:
            print("  🛑 Early stopping triggered!")
            break

    print("✅ Training completed successfully!")
    print(f"📁 Best model saved as: fixed_multihead_fabric_model_safe.pth")
    print(f"🎯 Final validation loss: {best_val_loss:.4f}")
    
    # Also create a converter for the old model if it exists
    convert_old_model_to_safe_format()

def convert_old_model_to_safe_format():
    """Convert old model to new safe format if it exists"""
    old_path = "fixed_multihead_fabric_model.pth"
    new_path = "fixed_multihead_fabric_model_safe.pth"
    
    if os.path.exists(old_path) and not os.path.exists(new_path):
        print(f"\n🔄 Converting old model to safe format...")
        try:
            # Load old model with weights_only=False
            old_checkpoint = torch.load(old_path, map_location='cpu', weights_only=False)
            
            # Convert numpy arrays to tensors
            if "semantic_means" in old_checkpoint and isinstance(old_checkpoint["semantic_means"], np.ndarray):
                old_checkpoint["semantic_means"] = torch.tensor(old_checkpoint["semantic_means"])
            if "semantic_stds" in old_checkpoint and isinstance(old_checkpoint["semantic_stds"], np.ndarray):
                old_checkpoint["semantic_stds"] = torch.tensor(old_checkpoint["semantic_stds"])
            
            # Save in safe format
            torch.save(old_checkpoint, new_path, _use_new_zipfile_serialization=True)
            print(f"✅ Converted old model to safe format: {new_path}")
            
        except Exception as e:
            print(f"❌ Failed to convert old model: {e}")

if __name__ == "__main__":
    train_model_fixed()