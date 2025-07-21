#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
讯飞超拟人TTS语音面试客户端
基于讯飞超拟人语音合成API，提供稳定的面试语音功能
"""

import os
import sys
import json
import base64
import hashlib
import hmac
import time
import threading
import logging
import tempfile
import websocket
import ssl
from pathlib import Path
from datetime import datetime
from time import mktime
from urllib.parse import urlencode
from wsgiref.handlers import format_date_time
from typing import Optional, List, Dict, Any, Callable

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent.parent
sys.path.append(str(project_root))

try:
    import pygame
except ImportError:
    pygame = None

from question_modes import get_question_mode_manager, MODE_INTERVIEW

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class XunfeiTTSParam:
    """讯飞超拟人TTS参数配置类"""

    def __init__(self, app_id: str, api_key: str, api_secret: str, text: str, voice: str = "x5_lingyuyan_flow"):
        """
        初始化超拟人TTS参数

        Args:
            app_id: 讯飞应用ID
            api_key: API密钥
            api_secret: API密钥
            text: 要合成的文本
            voice: 发音人参数
        """
        # 参数验证和None值检查
        self.app_id = app_id if app_id else "XXXXXXXX"
        self.api_key = api_key if api_key else "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.api_secret = api_secret if api_secret else "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        # 确保text不为空且为字符串
        if not text or not isinstance(text, str):
            self.text = "测试文本"
        else:
            self.text = text.strip() if text.strip() else "测试文本"
        self.voice = voice if voice else "x5_lingyuyan_flow"

        # 协议头部 - 超拟人TTS格式
        self.header = {
            "app_id": self.app_id,
            "status": 2  # 请求状态：0开始, 1中间, 2结束
        }

        # 能力参数 - 超拟人TTS格式（x5系列发音人不支持oral配置）
        self.parameter = {
            "tts": {
                "vcn": self.voice,  # 发音人参数
                "speed": 50,        # 语速：0-100
                "volume": 50,       # 音量：0-100
                "pitch": 50,        # 语调：0-100
                "bgs": 0,           # 背景音：0无背景音
                "reg": 0,           # 英文发音方式：0自动判断
                "rdn": 0,           # 数字发音方式：0自动判断
                "rhy": 0,           # 是否返回拼音标注：0不返回
                "audio": {
                    "encoding": "lame",      # 音频编码格式 (mp3)
                    "sample_rate": 24000,    # 采样率
                    "channels": 1,           # 声道数
                    "bit_depth": 16,         # 位深
                    "frame_size": 0          # 帧大小
                }
            }
        }

        # 输入数据段 - 超拟人TTS格式
        try:
            # 确保文本不为空并正确编码
            text_to_encode = self.text
            if not text_to_encode or not isinstance(text_to_encode, str):
                text_to_encode = "测试文本"
                logger.warning(f"文本为空或无效，使用默认文本: {text_to_encode}")

            encoded_text = str(base64.b64encode(text_to_encode.encode('utf-8')), "UTF8")

            self.payload = {
                "text": {
                    "encoding": "utf8",     # 文本编码
                    "compress": "raw",      # 文本压缩格式
                    "format": "plain",      # 文本格式
                    "status": 2,            # 数据状态：0开始, 1中间, 2结束
                    "seq": 0,               # 数据序号
                    "text": encoded_text    # base64编码的文本
                }
            }
        except Exception as e:
            logger.error(f"文本编码失败: {e}")
            # 使用默认文本的安全编码
            try:
                default_text = "测试文本"
                encoded_text = str(base64.b64encode(default_text.encode('utf-8')), "UTF8")
                self.payload = {
                    "text": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "plain",
                        "status": 2,
                        "seq": 0,
                        "text": encoded_text
                    }
                }
            except Exception as fallback_e:
                logger.error(f"默认文本编码也失败: {fallback_e}")
                # 最后的备用方案
                self.payload = {
                    "text": {
                        "encoding": "utf8",
                        "compress": "raw",
                        "format": "plain",
                        "status": 2,
                        "seq": 0,
                        "text": "5rWL6K+V5paH5pys"  # "测试文本"的base64编码
                    }
                }

class XunfeiTTSClient:
    """讯飞超拟人TTS客户端"""

    def __init__(self, app_id: str, api_key: str, api_secret: str, voice: str = "x5_lingyuyan_flow"):
        """
        初始化讯飞超拟人TTS客户端

        Args:
            app_id: 讯飞应用ID
            api_key: API密钥
            api_secret: API密钥
            voice: 发音人参数
        """
        # 参数验证和None值检查
        self.app_id = app_id if app_id else "XXXXXXXX"
        self.api_key = api_key if api_key else "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.api_secret = api_secret if api_secret else "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
        self.voice = voice if voice else "x5_lingyuyan_flow"

        # 使用超拟人TTS的专用API端点（如果没有权限，可以切换到标准TTS）
        self.base_url = "wss://cbm01.cn-huabei-1.xf-yun.com/v1/private/mcd9m97e6"
        # 备用标准TTS端点：wss://tts-api.xfyun.cn/v2/tts
        
        # 音频文件管理
        self.temp_dir = Path(tempfile.gettempdir()) / "xunfei_tts"
        self.temp_dir.mkdir(exist_ok=True)
        
        # 初始化pygame音频
        if pygame:
            try:
                pygame.mixer.init()
            except Exception as e:
                logger.error(f"pygame音频初始化失败: {e}")
        
        # 问题模式管理
        self.question_manager = get_question_mode_manager()
        self.current_mode = None
        self.is_playing = False
        
        # WebSocket相关
        self.ws = None
        self.audio_data = []
        self.synthesis_complete = False
        self.synthesis_error = None
        
        logger.info(f"讯飞TTS客户端初始化完成，发音人: {voice}")
    
    def _parse_url(self, request_url: str) -> tuple:
        """解析URL"""
        stidx = request_url.index("://")
        host = request_url[stidx + 3:]
        schema = request_url[:stidx + 3]
        edidx = host.index("/")
        if edidx <= 0:
            raise Exception("invalid request url:" + request_url)
        path = host[edidx:]
        host = host[:edidx]
        return host, path, schema
    
    def _assemble_ws_auth_url(self, request_url: str, method: str = "GET") -> str:
        """构建WebSocket认证URL"""
        host, path, schema = self._parse_url(request_url)
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        
        signature_origin = f"host: {host}\ndate: {date}\n{method} {path} HTTP/1.1"
        signature_sha = hmac.new(
            self.api_secret.encode('utf-8'),
            signature_origin.encode('utf-8'),
            digestmod=hashlib.sha256
        ).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        
        authorization_origin = f'api_key="{self.api_key}", algorithm="hmac-sha256", headers="host date request-line", signature="{signature_sha}"'
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }
        
        return request_url + "?" + urlencode(values)
    
    def _on_message(self, ws, message):
        """WebSocket消息处理 - 超拟人TTS格式"""
        try:
            message = json.loads(message)

            # 超拟人TTS响应格式：header + payload
            header = message.get("header", {})
            payload = message.get("payload", {})

            code = header.get("code", 0)
            message_text = header.get("message", "")
            sid = header.get("sid", "")
            status = header.get("status", 0)

            logger.info(f"收到消息: code={code}, sid={sid}, status={status}")

            if code != 0:
                self.synthesis_error = f"TTS合成错误: {message_text} (code: {code})"
                logger.error(self.synthesis_error)
                ws.close()
                return

            # 处理音频数据
            if "audio" in payload:
                audio_info = payload["audio"]
                audio_data = audio_info.get("audio", "")
                audio_status = audio_info.get("status", 0)

                if audio_data:
                    try:
                        audio_bytes = base64.b64decode(audio_data)
                        logger.info(f"收到音频数据: {len(audio_bytes)} bytes, status={audio_status}")
                        # 收集音频数据
                        self.audio_data.append(audio_bytes)
                    except Exception as decode_e:
                        logger.error(f"音频数据解码失败: {decode_e}")

                # 检查合成状态
                if audio_status == 2 or status == 2:  # 合成完成
                    self.synthesis_complete = True
                    logger.info("TTS合成完成")
                    ws.close()
            else:
                logger.info(f"收到非音频消息: {message}")

        except Exception as e:
            self.synthesis_error = f"消息处理异常: {e}"
            logger.error(self.synthesis_error)
    
    def _on_error(self, ws, error):
        """WebSocket错误处理"""
        self.synthesis_error = f"WebSocket错误: {error}"
        logger.error(self.synthesis_error)
    
    def _on_close(self, ws, close_status_code, close_msg):
        """WebSocket关闭处理"""
        logger.info("WebSocket连接已关闭")
    
    def _on_open(self, ws, tts_param):
        """WebSocket连接建立处理 - 超拟人TTS格式"""
        def run():
            try:
                # 超拟人TTS请求格式：header + parameter + payload
                data = {
                    "header": tts_param.header,
                    "parameter": tts_param.parameter,
                    "payload": tts_param.payload
                }

                request_json = json.dumps(data)
                logger.info(f"发送TTS请求: {request_json[:200]}...")
                ws.send(request_json)
                logger.info("超拟人TTS请求已发送")
            except Exception as e:
                self.synthesis_error = f"发送请求失败: {e}"
                logger.error(self.synthesis_error)
                ws.close()

        threading.Thread(target=run).start()
    
    def text_to_speech(self, text: str, output_file: Optional[str] = None) -> Optional[str]:
        """
        文本转语音 - 超拟人TTS

        Args:
            text: 要转换的文本
            output_file: 输出文件路径

        Returns:
            生成的音频文件路径
        """
        try:
            # 加强输入验证和None值检查
            if text is None:
                logger.error("文本输入为None")
                return None

            if not isinstance(text, str):
                logger.error(f"文本输入类型错误: {type(text)}, 期望str")
                return None

            text = text.strip()
            if not text:
                logger.error("文本为空或只包含空白字符")
                return None

            # 验证API参数
            if not self.app_id or self.app_id == "XXXXXXXX":
                logger.error("无效的app_id")
                return None

            if not self.api_key or self.api_key == "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
                logger.error("无效的api_key")
                return None

            if not self.api_secret or self.api_secret == "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX":
                logger.error("无效的api_secret")
                return None

            if not output_file:
                output_file = self.temp_dir / f"tts_{int(time.time())}.mp3"

            # 重置状态
            self.audio_data = []
            self.synthesis_complete = False
            self.synthesis_error = None

            logger.info(f"开始TTS合成: {text[:50]}...")

            # 创建超拟人TTS参数
            tts_param = XunfeiTTSParam(self.app_id, self.api_key, self.api_secret, text, self.voice)

            # 构建认证URL
            ws_url = self._assemble_ws_auth_url(self.base_url)
            logger.info(f"WebSocket URL: {ws_url[:100]}...")

            # 创建WebSocket连接
            websocket.enableTrace(False)
            self.ws = websocket.WebSocketApp(
                ws_url,
                on_message=self._on_message,
                on_error=self._on_error,
                on_close=self._on_close
            )
            
            # 设置连接建立回调
            self.ws.on_open = lambda ws: self._on_open(ws, tts_param)
            
            # 启动WebSocket连接（添加超时）
            import threading

            def run_websocket():
                try:
                    self.ws.run_forever(sslopt={"cert_reqs": ssl.CERT_NONE})
                except Exception as e:
                    self.synthesis_error = f"WebSocket运行错误: {e}"
                    logger.error(self.synthesis_error)

            ws_thread = threading.Thread(target=run_websocket)
            ws_thread.daemon = True
            ws_thread.start()

            # 等待合成完成，最多等待30秒
            timeout = 30
            start_time = time.time()
            while not self.synthesis_complete and not self.synthesis_error:
                if time.time() - start_time > timeout:
                    self.synthesis_error = "TTS合成超时"
                    break
                time.sleep(0.1)

            # 确保WebSocket关闭
            if self.ws:
                self.ws.close()

            # 检查合成结果
            if self.synthesis_error:
                logger.error(f"TTS合成失败: {self.synthesis_error}")
                return None

            if not self.synthesis_complete or not self.audio_data:
                logger.error("TTS合成未完成或无音频数据")
                return None
            
            # 保存音频文件
            with open(output_file, 'wb') as f:
                for audio_chunk in self.audio_data:
                    f.write(audio_chunk)
            
            logger.info(f"TTS生成完成: {text[:50]}...")
            return str(output_file)
            
        except Exception as e:
            logger.error(f"TTS生成失败: {e}")
            return None
    
    def play_audio(self, audio_file: str) -> bool:
        """
        播放音频文件
        
        Args:
            audio_file: 音频文件路径
            
        Returns:
            播放是否成功
        """
        try:
            if not pygame:
                logger.error("pygame未安装，无法播放音频")
                return False
                
            if not os.path.exists(audio_file):
                logger.error(f"音频文件不存在: {audio_file}")
                return False
            
            self.is_playing = True
            pygame.mixer.music.load(audio_file)
            pygame.mixer.music.play()
            
            # 等待播放完成
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            self.is_playing = False
            logger.info(f"音频播放完成: {audio_file}")
            return True
            
        except Exception as e:
            logger.error(f"音频播放失败: {e}")
            self.is_playing = False
            return False
    
    def speak_text(self, text: str) -> bool:
        """
        直接说出文本（TTS + 播放）
        
        Args:
            text: 要说出的文本
            
        Returns:
            是否成功
        """
        try:
            # 生成语音
            audio_file = self.text_to_speech(text)
            if not audio_file:
                return False
            
            # 播放语音
            success = self.play_audio(audio_file)
            
            # 清理临时文件
            try:
                os.remove(audio_file)
            except:
                pass
            
            return success
            
        except Exception as e:
            logger.error(f"语音播放失败: {e}")
            return False
    
    def set_question_mode(self, mode_id: str) -> bool:
        """
        设置问题模式
        
        Args:
            mode_id: 问题模式ID
            
        Returns:
            设置是否成功
        """
        mode = self.question_manager.get_mode(mode_id)
        if mode:
            self.current_mode = mode
            logger.info(f"问题模式设置为: {mode.name}")
            return True
        else:
            logger.error(f"问题模式不存在: {mode_id}")
            return False
    
    def start_interview(self, mode_id: str = MODE_INTERVIEW) -> bool:
        """
        开始面试

        Args:
            mode_id: 问题模式ID

        Returns:
            是否成功开始
        """
        try:
            # 设置问题模式
            if not self.set_question_mode(mode_id):
                return False

            # 开场白 - 暂时跳过语音播放，直接返回成功
            logger.info("面试会话创建成功，跳过开场白语音")

            # 直接返回成功，让前端处理语音播放
            return True

        except Exception as e:
            logger.error(f"开始面试失败: {e}")
            return False
    
    def ask_next_question(self) -> bool:
        """
        问下一个问题

        Returns:
            是否还有问题
        """
        try:
            if not self.current_mode:
                logger.error("未设置问题模式")
                return False

            if self.current_mode.is_completed:
                # 面试结束
                logger.info("面试已完成")
                return False

            # 获取下一个问题
            question = self.current_mode.get_next_question()
            if question:
                logger.info(f"准备提问: {question}")
                return True
            else:
                logger.info("没有更多问题")
                return False

        except Exception as e:
            logger.error(f"提问失败: {e}")
            return False
    
    def mark_question_answered(self) -> None:
        """标记当前问题已回答"""
        if self.current_mode:
            self.current_mode.mark_current_answered()
            logger.info("当前问题已标记为已回答")
    
    def get_interview_progress(self) -> Dict[str, Any]:
        """
        获取面试进度
        
        Returns:
            面试进度信息
        """
        if not self.current_mode:
            return {"error": "未设置问题模式"}
        
        return {
            "mode_name": self.current_mode.name,
            "current_index": self.current_mode.current_index,
            "total_questions": len(self.current_mode.questions),
            "is_completed": self.current_mode.is_completed,
            "progress_percentage": (self.current_mode.current_index / len(self.current_mode.questions)) * 100
        }
    
    def cleanup(self) -> None:
        """清理资源"""
        try:
            # 停止音频播放
            if pygame:
                pygame.mixer.music.stop()
                pygame.mixer.quit()
            
            # 关闭WebSocket连接
            if self.ws:
                self.ws.close()
            
            # 清理临时文件
            for file in self.temp_dir.glob("tts_*.mp3"):
                try:
                    file.unlink()
                except:
                    pass
            
            logger.info("讯飞TTS客户端资源清理完成")
            
        except Exception as e:
            logger.error(f"资源清理失败: {e}")


# 面试控制器（保持与之前相同的接口）
class InterviewController:
    """面试控制器"""
    
    def __init__(self, app_id: str = "06159011", api_key: str = "4c71a0e8ef0d22a01315ee0056fd78c2", api_secret: str = "MGFhOWFjNThkNDRjNTUxZjM2YjNhMDA0"):
        """初始化面试控制器"""
        self.tts_client = XunfeiTTSClient(app_id, api_key, api_secret)
        self.is_active = False
        self.current_session_id = None
        
    def create_session(self, session_id: str, mode_id: str = MODE_INTERVIEW) -> Dict[str, Any]:
        """
        创建面试会话
        
        Args:
            session_id: 会话ID
            mode_id: 问题模式ID
            
        Returns:
            会话创建结果
        """
        try:
            self.current_session_id = session_id
            self.is_active = True
            
            # 开始面试
            success = self.tts_client.start_interview(mode_id)
            
            return {
                "success": success,
                "session_id": session_id,
                "message": "面试会话创建成功" if success else "面试会话创建失败"
            }
            
        except Exception as e:
            logger.error(f"创建面试会话失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def handle_user_response(self, session_id: str, response_text: str = None) -> Dict[str, Any]:
        """
        处理用户回答
        
        Args:
            session_id: 会话ID
            response_text: 用户回答文本（可选）
            
        Returns:
            处理结果
        """
        try:
            if session_id != self.current_session_id:
                return {"success": False, "error": "会话ID不匹配"}
            
            if not self.is_active:
                return {"success": False, "error": "面试会话未激活"}
            
            # 标记当前问题已回答
            self.tts_client.mark_question_answered()
            
            # 问下一个问题
            has_next = self.tts_client.ask_next_question()
            
            if not has_next:
                self.is_active = False
            
            return {
                "success": True,
                "has_next_question": has_next,
                "progress": self.tts_client.get_interview_progress()
            }
            
        except Exception as e:
            logger.error(f"处理用户回答失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def end_session(self, session_id: str) -> Dict[str, Any]:
        """
        结束面试会话
        
        Args:
            session_id: 会话ID
            
        Returns:
            结束结果
        """
        try:
            if session_id == self.current_session_id:
                self.is_active = False
                self.current_session_id = None
                self.tts_client.cleanup()
                
                return {
                    "success": True,
                    "message": "面试会话已结束"
                }
            else:
                return {
                    "success": False,
                    "error": "会话ID不匹配"
                }
                
        except Exception as e:
            logger.error(f"结束面试会话失败: {e}")
            return {
                "success": False,
                "error": str(e)
            }

# 全局面试控制器实例
interview_controller = None

def get_interview_controller(app_id: str = None, api_key: str = None, api_secret: str = None) -> InterviewController:
    """
    获取面试控制器实例

    Args:
        app_id: 讯飞应用ID
        api_key: API密钥
        api_secret: API密钥

    Returns:
        面试控制器实例
    """
    global interview_controller
    if interview_controller is None:
        # 如果没有传递参数，使用默认值而不是None
        if app_id is None:
            app_id = "06159011"
        if api_key is None:
            api_key = "4c71a0e8ef0d22a01315ee0056fd78c2"
        if api_secret is None:
            api_secret = "MGFhOWFjNThkNDRjNTUxZjM2YjNhMDA0"
        interview_controller = InterviewController(app_id, api_key, api_secret)
    return interview_controller
