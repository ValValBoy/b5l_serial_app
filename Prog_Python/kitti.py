import torch
import flash
from flash.core.data.utils import download_data
from flash.pointcloud import PointCloudObjectDetector, PointCloudObjectDetectorData
from flash.image import ImageClassifier
from flash.image import SemanticSegmentation


# Create the DataModule

download_data("https://pl-flash-data.s3.amazonaws.com/KITTI_tiny.zip", "data/")

datamodule = PointCloudObjectDetectorData.from_folders(
    train_folder="data/KITTI_Tiny/Kitti/train",
    val_folder="data/KITTI_Tiny/Kitti/val",
    batch_size=4,
)

# Build the task
model = PointCloudObjectDetector(backbone="pointpillars_kitti", num_classes=datamodule.num_classes)

# Creeate the trainer and finetune the model
trainer = flash.Trainer(
    max_epochs=1, limit_train_batches=1, limit_val_batches=1, num_sanity_val_steps=0, gpus=torch.cuda.device_count()
)
trainer.fit(model, datamodule)

# Predict what's within a few PointClouds?
datamodule = PointCloudObjectDetectorData.from_files(
    predict_files=[
        "data/KITTI_Tiny/Kitti/predict/scans/000000.bin",
        "data/KITTI_Tiny/Kitti/predict/scans/000001.bin",
    ],
    batch_size=4,
)
predictions = trainer.predict(model, datamodule=datamodule)
print(predictions)

# Save the model
trainer.save_checkpoint("pointcloud_detection_model.pt")

# get the backbones available for ImageClassifier
backbones = ImageClassifier.available_backbones()

# print the backbones
print(backbones)

# get the heads available for SemanticSegmentation
heads = SemanticSegmentation.available_heads()

# print the heads
print(heads)