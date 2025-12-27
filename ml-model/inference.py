import torch
import torch.nn as nn
from torchvision import transforms, models
from PIL import Image
import json

# -------------------------
# Model
# -------------------------
class MultiHeadNet(nn.Module):
    def __init__(self, num_parts, num_defects, semantic_dim):
        super().__init__()
        base = models.resnet18(weights=None)
        self.backbone = nn.Sequential(*list(base.children())[:-1])
        feat_dim = base.fc.in_features
        self.part_head = nn.Linear(feat_dim, num_parts)
        self.defect_head = nn.Linear(feat_dim, num_defects)
        self.semantic_head = nn.Linear(feat_dim, semantic_dim)

    def forward(self, x):
        x = self.backbone(x)
        x = torch.flatten(x, 1)
        return self.part_head(x), self.defect_head(x), self.semantic_head(x)

# -------------------------
# Load Model
# -------------------------
def load_model(model_path="multihead_fabric_model.pth"):
    checkpoint = torch.load(model_path, map_location="cpu")
    model = MultiHeadNet(len(checkpoint["part_to_idx"]),
                         len(checkpoint["defect_to_idx"]),
                         checkpoint["semantic_dim"])
    model.load_state_dict(checkpoint["model_state"])
    model.eval()
    return model, checkpoint

# -------------------------
# Prediction
# -------------------------
transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
])

def predict(image_path, model, checkpoint):
    img = Image.open(image_path).convert("RGB")
    img_t = transform(img).unsqueeze(0)

    with torch.no_grad():
        part_out, defect_out, semantic_out = model(img_t)
        part_idx = torch.argmax(part_out, dim=1).item()
        defect_idx = torch.argmax(defect_out, dim=1).item()
        semantic_pred = semantic_out.squeeze().tolist()

    part_label = {v: k for k, v in checkpoint["part_to_idx"].items()}[part_idx]
    defect_label = {v: k for k, v in checkpoint["defect_to_idx"].items()}[defect_idx]

    return {
        "fabric_part": part_label,
        "defect_type": defect_label,
        "semantic": {
            "area_used": float(semantic_pred[0]),
            "utilization": float(semantic_pred[1])
        }
    }

if __name__ == "__main__":
    model, checkpoint = load_model("multihead_fabric_model.pth")
    test_image = "fabric_dataset/train/images/train_0000.png"
    result = predict(test_image, model, checkpoint)
    print(json.dumps(result, indent=2))
