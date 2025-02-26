# Variables
DOCKER_REGISTRY=crpi-qha9zod7jj1h7qwo.cn-beijing.personal.cr.aliyuncs.com/dify-ns
YOLO_IMAGE=$(DOCKER_REGISTRY)/label-studio-yolov8-backend
VERSION=latest

# Build Docker images
build-yolov8:
	@echo "Building web Docker image: $(YOLO_IMAGE):$(VERSION)..."
	docker build -t $(YOLO_IMAGE):$(VERSION) .
	@echo "Web Docker image built successfully: $(YOLO_IMAGE):$(VERSION)"

# Push Docker images
push-yolov8:
	@echo "Pushing web Docker image: $(YOLO_IMAGE):$(VERSION)..."
	docker push $(YOLO_IMAGE):$(VERSION)
	@echo "Web Docker image pushed successfully: $(YOLO_IMAGE):$(VERSION)"

build-push: build-yolov8 push-yolov8
	@echo "All Docker images have been built and pushed."

# Phony targets
.PHONY: build-yolov8 push-yolov8 build-push
