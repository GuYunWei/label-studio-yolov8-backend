from label_studio_ml.model import LabelStudioMLBase
import requests, os
from ultralytics import YOLO
from PIL import Image
from io import BytesIO

LS_URL = os.environ['LABEL_STUDIO_BASEURL']
LS_API_TOKEN = os.environ['LABEL_STUDIO_API_TOKEN']

class YOLOv8Model(LabelStudioMLBase):
    def __init__(self, **kwargs):
        # Call base class constructor
        super(YOLOv8Model, self).__init__(**kwargs)

        from_name, schema = list(self.parsed_label_config.items())[0]
        self.from_name = from_name
        self.to_name = schema['to_name'][0]
        self.labels = ['table图表', '图+描述', '图片', '描述']
        self.model = YOLO("best.pt")

    def predict(self, tasks, **kwargs):
        """ This is where inference happens: model returns 
            the list of predictions based on input list of tasks 
        """
        task = tasks[0]

        predictions = []
        score = 0

        header = {
            "Authorization": "Token " + LS_API_TOKEN}

        # 下载图像
        try:
            response = requests.get(LS_URL + task['data']['image'], headers=header)
            response.raise_for_status()  # 如果返回错误，抛出异常
            image_data = response.content
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch image: {e}")
            return []

        # 尝试打开图像
        try:
            image = Image.open(BytesIO(image_data))
        except Exception as e:
            print(f"Error opening image: {e}")
            return []

        original_width, original_height = image.size
        results = self.model.predict(image)

        i = 0
        for result in results:
            for i, prediction in enumerate(result.boxes):
                xyxy = prediction.xyxy[0].tolist()
                predictions.append({
                    "id": str(i),
                    "from_name": self.from_name,
                    "to_name": self.to_name,
                    "type": "rectanglelabels",
                    "score": prediction.conf.item(),
                    "original_width": original_width,
                    "original_height": original_height,
                    "image_rotation": 0,
                    "value": {
                        "rotation": 0,
                        "x": xyxy[0] / original_width * 100, 
                        "y": xyxy[1] / original_height * 100,
                        "width": (xyxy[2] - xyxy[0]) / original_width * 100,
                        "height": (xyxy[3] - xyxy[1]) / original_height * 100,
                        "rectanglelabels": [self.labels[int(prediction.cls.item())]]
                    }
                })
                score += prediction.conf.item()
            
        return [{
            "result": predictions,
            "score": score / (i + 1),
            "model_version": "v8n",  # all predictions will be differentiated by model version
        }]
