"""
情感分析器模块，基于EfficientFace实现情绪识别
"""

import os
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms
from PIL import Image
import cv2
import numpy as np
import time
import base64
from flask import current_app
from models.EfficientFace import efficient_face

# 英文情绪标签到中文情绪标签的映射
# EfficientFace使用RAF-DB数据集的标签顺序: 0: Neutral; 1: Happiness; 2: Sadness; 3: Surprise; 4: Fear; 5: Disgust; 6: Anger
EMOTION_LABELS_CN = {
    'neutral': '中性',
    'happiness': '微笑',
    'sadness': '悲伤',
    'surprise': '惊讶',
    'fear': '恐惧',
    'disgust': '厌恶',
    'anger': '生气'
}

# RAF-DB数据集的标签顺序对应的索引映射
EMOTION_INDEX_TO_LABEL = {
    0: 'neutral',
    1: 'happiness',
    2: 'sadness',
    3: 'surprise',
    4: 'fear',
    5: 'disgust',
    6: 'anger'
}

# 全局情感分析器实例
_emotion_analyzer_instance = None


class EmotionClassifier:
    """情绪分类器，基于EfficientFace"""
    
    def __init__(self, model_path, device='cpu'):
        """
        初始化情绪分类器
        
        Args:
            model_path: 模型权重文件路径
            device: 设备，可以是'cpu'或'cuda'
        """
        self.device = device
        self.class_names = list(EMOTION_INDEX_TO_LABEL.values())
        self.model = self.load_model(model_path)
        self.transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
            transforms.Normalize(mean=[0.57535914, 0.44928582, 0.40079932],
                                 std=[0.20735591, 0.18981615, 0.18132027])
        ])

    def load_model(self, model_path):
        """
        加载模型
        
        Args:
            model_path: 模型权重文件路径
            
        Returns:
            加载的模型
        """
        model = efficient_face()
        model.fc = nn.Linear(1024, len(self.class_names))  # 7个情绪类别
        
        # 加载预训练权重
        try:
            checkpoint = torch.load(model_path, map_location=self.device)
            
            # 处理不同格式的检查点
            if 'state_dict' in checkpoint:
                state_dict = checkpoint['state_dict']
            else:
                state_dict = checkpoint
                
            # 处理带有"module."前缀的权重
            from collections import OrderedDict
            new_state_dict = OrderedDict()
            for k, v in state_dict.items():
                if k.startswith('module.'):
                    name = k[7:]  # 去掉"module."前缀
                else:
                    name = k
                new_state_dict[name] = v
                
            model.load_state_dict(new_state_dict)
        except Exception as e:
            # 如果加载失败，尝试使用默认的emotion.pth
            print(f"加载EfficientFace模型失败: {e}，尝试使用默认模型")
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            default_model_path = os.path.join(base_dir, 'weights', 'emotion.pth')
            
            # 创建一个简单的MobileNetV2模型作为备用
            import torchvision.models as models
            model = models.mobilenet_v2(pretrained=False)
            model.classifier[1] = nn.Linear(model.last_channel, len(self.class_names))
            model.load_state_dict(torch.load(default_model_path, map_location=self.device))
            
        model.eval()
        model.to(self.device)
        return model

    def predict_image(self, image):
        """
        预测图像的情绪
        
        Args:
            image: PIL Image对象
            
        Returns:
            tuple: (预测的情绪类别, 置信度)
        """
        image = self.transform(image).unsqueeze(0).to(self.device)
        with torch.no_grad():
            outputs = self.model(image)
            # 获取所有类别的概率
            probs = F.softmax(outputs, dim=1)[0]
            _, predicted = torch.max(outputs, 1)
            
        predicted_class = self.class_names[predicted.item()]
        confidence = probs[predicted.item()].item()
        
        # 获取所有情绪的概率分布
        emotion_scores = {emotion: probs[i].item() for i, emotion in enumerate(self.class_names)}
        
        return predicted_class, confidence, emotion_scores


class EmotionAnalyzer:
    """
    情感分析器类，用于处理图像和检测情绪
    """
    
    def __init__(self, model_path=None, device='cpu', scale_factor=0.5, debug_mode=False):
        """
        初始化情感分析器
        
        Args:
            model_path: 模型权重文件路径，如果为None则使用默认路径
            device: 设备，可以是'cpu'或'cuda'
            scale_factor: 图像缩放因子，用于加速处理
            debug_mode: 是否开启调试模式
        """
        if model_path is None:
            # 使用默认模型路径
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            model_path = os.path.join(base_dir, 'weights', 'model_best.pth.tar')
            
            # 如果新模型不存在，使用备用模型
            if not os.path.exists(model_path):
                model_path = os.path.join(base_dir, 'weights', 'efficientface.pth.tar')
                
                # 如果备用模型也不存在，使用原始模型
                if not os.path.exists(model_path):
                    model_path = os.path.join(base_dir, 'weights', 'emotion.pth')
                
        if debug_mode:
            print(f"使用模型路径: {model_path}")
            
        self.classifier = EmotionClassifier(model_path, device)
        self.scale_factor = scale_factor
        self.debug_mode = debug_mode
        
        # 加载OpenCV人脸检测器
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        
        # 情绪颜色映射
        self.emotion_colors = {
            'anger': (0, 0, 255),      # 红色
            'disgust': (0, 255, 0),    # 绿色
            'fear': (255, 0, 255),     # 紫色
            'happiness': (0, 255, 255),    # 黄色
            'neutral': (255, 255, 255), # 白色
            'sadness': (255, 0, 0),        # 蓝色
            'surprise': (0, 165, 255)  # 橙色
        }
        
        # 统计计数
        self.emotion_stats = {emotion: 0 for emotion in self.classifier.class_names}
        self.total_frames = 0
        self.processed_frames = 0
        self.start_time = time.time()
        
        # 当前表情状态
        self.current_emotion = {
            'main_emotion': 'neutral',
            'cn_emotion': EMOTION_LABELS_CN.get('neutral', 'neutral'),
            'confidence': 0.0,
            'timestamp': time.time(),
            'detailed_emotions': {emotion: 0.0 for emotion in self.classifier.class_names}
        }
        
        if self.debug_mode:
            print(f"情感分析器初始化完成，使用模型: {model_path}")
    
    def process_frame(self, frame, visualization_mode='basic'):
        """
        处理单个图像帧，检测人脸并分析情绪
        
        Args:
            frame: OpenCV格式的图像帧
            visualization_mode: 已废弃参数，保留仅用于兼容，始终使用基本可视化
            
        Returns:
            tuple: (处理后的图像, 结果字典)
        """
        if frame is None:
            return None, {"error": "无效的输入帧"}
        
        # 创建结果副本
        processed_frame = frame.copy()
        results = {
            "face_count": 0,
            "expressions": []
        }
        
        # 调整帧大小以加快处理速度
        if self.scale_factor != 1.0:
            small_frame = cv2.resize(frame, (0, 0), fx=self.scale_factor, fy=self.scale_factor)
        else:
            small_frame = frame.copy()
            
        # 转换为灰度图进行人脸检测
        gray = cv2.cvtColor(small_frame, cv2.COLOR_BGR2GRAY)
        
        # 检测人脸
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.1, 
            minNeighbors=5, 
            minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
        
        # 更新人脸数量
        results["face_count"] = len(faces)
        
        # 处理检测到的人脸
        for face_idx, (x, y, w, h) in enumerate(faces):
            # 调整回原始比例
            if self.scale_factor != 1.0:
                x = int(x / self.scale_factor)
                y = int(y / self.scale_factor)
                w = int(w / self.scale_factor)
                h = int(h / self.scale_factor)
            
            # 在原始帧上提取人脸区域
            face_roi = frame[y:y+h, x:x+w]
            
            # 转换为PIL图像进行情感分析
            pil_img = Image.fromarray(cv2.cvtColor(face_roi, cv2.COLOR_BGR2RGB))
            
            try:
                # 预测情感
                emotion, confidence, emotion_scores = self.classifier.predict_image(pil_img)
                self.processed_frames += 1
                self.emotion_stats[emotion] += 1
                
                # 更新当前表情状态（只处理第一个检测到的人脸）
                if face_idx == 0:
                    # 更新当前表情
                    self.current_emotion = {
                        'main_emotion': emotion,
                        'cn_emotion': EMOTION_LABELS_CN.get(emotion, emotion),
                        'confidence': confidence,
                        'timestamp': time.time(),
                        'detailed_emotions': emotion_scores
                    }
                
                # 将结果添加到列表
                results["expressions"].append({
                    "face_id": face_idx,
                    "expression": EMOTION_LABELS_CN.get(emotion, emotion),
                    "confidence": confidence,
                    "details": {
                        "en_emotion": emotion,
                        "scores": {EMOTION_LABELS_CN.get(e, e): float(emotion_scores[e]) for e in self.classifier.class_names}
                    }
                })
                
                # 在帧上标记人脸和情感（始终显示）
                color = self.emotion_colors.get(emotion, (255, 255, 255))
                cv2.rectangle(processed_frame, (x, y), (x+w, y+h), color, 2)
                label = f"{EMOTION_LABELS_CN.get(emotion, emotion)}: {confidence:.2f}"
                cv2.putText(processed_frame, label, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)
            except Exception as e:
                if self.debug_mode:
                    print(f"处理人脸时出错: {e}")
                
        # 更新FPS计数
        self.total_frames += 1
        elapsed_time = time.time() - self.start_time
        fps = self.processed_frames / elapsed_time if elapsed_time > 0 else 0
        
        # 在帧上显示FPS
        if self.debug_mode:
            fps_text = f"FPS: {fps:.2f}"
            cv2.putText(processed_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        
        return processed_frame, results
    
    def get_emotion_distribution(self):
        """
        获取情绪分布统计
        
        Returns:
            dict: 情绪分布统计
        """
        total = sum(self.emotion_stats.values())
        if total == 0:
            return {emotion: 0 for emotion in self.emotion_stats}
        
        # 计算百分比
        distribution = {emotion: count / total for emotion, count in self.emotion_stats.items()}
        
        # 添加中文标签
        cn_distribution = {EMOTION_LABELS_CN.get(emotion, emotion): percentage 
                         for emotion, percentage in distribution.items()}
        
        # 添加处理统计信息
        elapsed_time = time.time() - self.start_time
        stats = {
            'distribution': cn_distribution,
            'total_frames': self.total_frames,
            'processed_frames': self.processed_frames,
            'elapsed_time': elapsed_time,
            'fps': self.processed_frames / elapsed_time if elapsed_time > 0 else 0
        }
        
        return stats
    
    def reset_stats(self):
        """重置统计信息"""
        self.emotion_stats = {emotion: 0 for emotion in self.classifier.class_names}
        self.total_frames = 0
        self.processed_frames = 0
        self.start_time = time.time()
        
    def get_current_emotion(self):
        """
        获取当前情绪
        
        Returns:
            dict: 当前情绪信息
        """
        return self.current_emotion


def get_emotion_analyzer(debug_mode=False):
    """
    获取情感分析器单例
    
    Args:
        debug_mode: 是否开启调试模式
        
    Returns:
        EmotionAnalyzer: 情感分析器实例
    """
    global _emotion_analyzer_instance
    
    if _emotion_analyzer_instance is None:
        try:
            # 获取模型路径
            model_path = None
            if current_app:
                model_path = current_app.config.get('EMOTION_MODEL_PATH')
                
            # 检查是否支持CUDA
            device = 'cuda' if torch.cuda.is_available() else 'cpu'
            
            # 创建情感分析器
            _emotion_analyzer_instance = EmotionAnalyzer(
                model_path=model_path,
                device=device,
                debug_mode=debug_mode
            )
            
            if debug_mode:
                print(f"情感分析器初始化成功，使用设备: {device}")
        except Exception as e:
            print(f"情感分析器初始化失败: {str(e)}")
            raise
    
    return _emotion_analyzer_instance


def analyze_emotion(video_data):
    """
    分析视频数据中的情绪
    
    Args:
        video_data: Base64编码的视频数据
        
    Returns:
        dict: 分析结果
    """
    try:
        # 解码视频数据
        video_bytes = base64.b64decode(video_data)
        video_np = np.frombuffer(video_bytes, np.uint8)
        
        # 创建视频捕获对象
        cap = cv2.VideoCapture()
        cap.open(video_np)
        
        if not cap.isOpened():
            return {
                "success": False,
                "message": "无法打开视频",
                "data": None
            }
        
        # 获取情感分析器
        analyzer = get_emotion_analyzer()
        
        # 处理视频帧
        frames_results = []
        frame_count = 0
        max_frames = 100  # 最多处理100帧
        
        while frame_count < max_frames:
            ret, frame = cap.read()
            if not ret:
                break
                
            # 每隔几帧处理一次
            if frame_count % 5 == 0:
                # 处理帧
                _, results = analyzer.process_frame(frame)
                frames_results.append(results)
                
            frame_count += 1
            
        # 释放资源
        cap.release()
        
        # 汇总结果
        all_expressions = []
        for frame_result in frames_results:
            if "expressions" in frame_result:
                all_expressions.extend(frame_result["expressions"])
                
        # 计算主要情绪
        emotion_counts = {}
        for expr in all_expressions:
            emotion = expr["expression"]
            if emotion not in emotion_counts:
                emotion_counts[emotion] = 0
            emotion_counts[emotion] += 1
            
        # 找出最常见的情绪
        main_emotion = max(emotion_counts.items(), key=lambda x: x[1])[0] if emotion_counts else "中性"
        
        return {
            "success": True,
            "message": "视频情绪分析完成",
            "data": {
                "main_emotion": main_emotion,
                "frame_count": frame_count,
                "processed_count": len(frames_results),
                "expressions": all_expressions[:10]  # 只返回前10个表情结果
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"视频情绪分析失败: {str(e)}",
            "data": None
        }


def get_emotion_distribution():
    """
    获取情绪分布统计
    
    Returns:
        dict: 情绪分布统计
    """
    analyzer = get_emotion_analyzer()
    return analyzer.get_emotion_distribution()


def reset_emotion_stats():
    """重置情绪统计"""
    analyzer = get_emotion_analyzer()
    analyzer.reset_stats()
    

def get_current_emotion():
    """
    获取当前情绪
    
    Returns:
        dict: 当前情绪信息
    """
    analyzer = get_emotion_analyzer()
    return analyzer.get_current_emotion() 