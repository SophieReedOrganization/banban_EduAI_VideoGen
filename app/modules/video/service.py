from app.core import Config, Logger, MongoDB
from .prompt import MANIM_SCRIPT_PROMPT, SPEECH_SCRIPT_PROMPT
from google.genai import types
from edge_tts import Communicate
from datetime import datetime, timezone
import tempfile, io, os, base64, asyncio, PIL.Image, shutil, glob

# 簡化版的階段性視頻生成，可以在任何階段停止並返回結果
async def process_video_until_stage(
    region: str,
    client_id: str,
    task_id: str,
    text: str,
    voice: str,
    image_base64: str,
    content: str,
    stop_at_stage: int = 7  # 1=動畫說明, 2=動畫腳本, 3=腳本檢查, 4=語音腳本, 5=視頻生成, 6=語音生成, 7=完整流程
):
    """
    在指定階段停止的視頻生成函數
    stop_at_stage: 1-7 對應不同的停止階段
    """
    text = text.replace("$", "$$")
    results = {}
    
    try:
        Logger.info(f"開始處理視頻生成直到階段 {stop_at_stage}, client_id: {client_id}, task_id: {task_id}")
        
        # 階段1: 生成動畫說明
        Logger.info(f"[階段1] 開始生成動畫說明...{datetime.now()}")
        animation_story = await generate_animation_story(text, voice, image_base64)
        results["animation_story"] = animation_story
        Logger.info(f"✓ 動畫說明生成完成，長度: {len(animation_story)} 字符")
        
        if stop_at_stage == 1:
            return {"stage": 1, "stage_name": "動畫說明", "result": animation_story, "all_results": results}
        
        # 階段2: 生成動畫腳本
        Logger.info(f"[階段2] 開始生成動畫腳本...{datetime.now()}")
        animation_script = await generate_manim_script(animation_story, voice, image_base64)
        results["animation_script"] = animation_script
        Logger.info(f"✓ 動畫腳本生成完成，長度: {len(animation_script)} 字符")
        
        if stop_at_stage == 2:
            return {"stage": 2, "stage_name": "動畫腳本", "result": animation_script, "all_results": results}
        
        # 階段3: 檢查動畫腳本
        Logger.info(f"[階段3] 開始檢查動畫腳本...{datetime.now()}")
        confirm_animation_script = await check_animation_script(animation_script)
        results["checked_script"] = confirm_animation_script
        Logger.info(f"✓ 動畫腳本檢查完成")
        
        if stop_at_stage == 3:
            return {"stage": 3, "stage_name": "腳本檢查", "result": confirm_animation_script, "all_results": results}
        
        # 階段4: 生成語音腳本
        Logger.info(f"[階段4] 開始生成語音腳本...{datetime.now()}")
        speech_script = await generate_speech_script(confirm_animation_script, voice)
        results["speech_script"] = speech_script
        Logger.info(f"✓ 語音腳本生成完成，長度: {len(speech_script)} 字符")
        
        if stop_at_stage == 4:
            return {"stage": 4, "stage_name": "語音腳本", "result": speech_script, "all_results": results}
        
        # 階段5: 生成視頻
        Logger.info(f"[階段5] 開始生成視頻...{datetime.now()}")
        video_path, video_duration, temp_video_dir = await generate_video(confirm_animation_script)
        results["video_info"] = {"path": video_path, "duration": video_duration, "temp_dir": temp_video_dir}
        Logger.info(f"✓ 視頻生成完成，時長: {video_duration:.2f}秒")
        
        if stop_at_stage == 5:
            return {"stage": 5, "stage_name": "視頻生成", "result": f"視頻已生成，時長: {video_duration:.2f}秒", "all_results": results}
        
        # 階段6: 生成語音
        Logger.info(f"[階段6] 開始生成語音...{datetime.now()}")
        audio_path, audio_duration = await generate_speech(speech_script, voice, task_id)
        results["audio_info"] = {"path": audio_path, "duration": audio_duration}
        Logger.info(f"✓ 語音生成完成，時長: {audio_duration:.2f}秒")
        
        if stop_at_stage == 6:
            return {"stage": 6, "stage_name": "語音生成", "result": f"語音已生成，時長: {audio_duration:.2f}秒", "all_results": results}
        
        # 階段7: 完整流程（原本的邏輯）
        Logger.info(f"[階段7] 繼續完整的視頻處理流程...")
        # 這裡可以繼續原本的合併、上傳等邏輯
        return {"stage": 7, "stage_name": "完整流程", "result": "繼續完整流程", "all_results": results}
        
    except Exception as e:
        Logger.error(f"階段 {stop_at_stage} 處理失敗: {str(e)}")
        return {"stage": stop_at_stage, "stage_name": f"階段{stop_at_stage}", "error": str(e), "all_results": results}

async def process_generate_educational_video(
    region: str,
    client_id: str,
    task_id: str,
    text: str,
    voice: str,
    image_base64: str,
    content: str
):
    temp_files = []  # 存儲所有臨時文件路徑
    temp_dirs = []   # 存儲所有臨時目錄路徑
    text = text.replace("$", "$$")
    animation_script = ""
    try:
        Logger.info(f"開始處理視頻生成, client_id: {client_id}, task_id: {task_id}.")
        Logger.info(f"[步驟1] 開始生成動畫說明...{datetime.now()}")
        animation_story = await generate_animation_story(text, voice, image_base64)
        Logger.info(f"[步驟2] 開始生成動畫腳本...{datetime.now()}")
        animation_script = await generate_manim_script(animation_story, voice, image_base64)
        Logger.info(f"✓ 動畫腳本生成完成，長度: {len(animation_script)} 字符")
        print(animation_script)
        Logger.info(f"[步驟3] 開始檢查動畫腳本...{datetime.now()}")
        confirm_animation_script = await check_animation_script(animation_script)
        print(confirm_animation_script)
        Logger.info(f"✓ 動畫腳本檢查完成 ✓")
        Logger.info(f"[步驟4] 開始生成語音腳本...{datetime.now()}")
        video_task = asyncio.create_task(generate_video(confirm_animation_script))
        speech_script = await generate_speech_script(confirm_animation_script, voice)
        Logger.info(f"✓ 語音腳本生成完成，長度: {len(speech_script)} 字符")
        speech_task = asyncio.create_task(generate_speech(speech_script, voice, task_id))
        
        # 等待兩個任務完成
        video_path, video_duration, temp_video_dir = await video_task
        audio_path, audio_duration = await speech_task
        
        temp_dirs.append(temp_video_dir)
        temp_files.append(video_path)  # 添加到臨時文件列表
        temp_files.append(audio_path)  # 添加到臨時文件列表
        
        Logger.info(f"✓ 音頻時長: {audio_duration:.2f}秒, 視頻時長: {video_duration:.2f}秒")
        if abs(video_duration - audio_duration) > 0.5:
            Logger.info(f"[步驟5] 調整視頻速度以匹配音頻時長...")
            speed_factor = audio_duration / video_duration
            temp_video = os.path.join(tempfile.gettempdir(), f"temp_video_{task_id}.mp4")
            
            # 確保視頻文件存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"視頻文件不存在: {video_path}")
            
            # 使用絕對路徑
            video_path_abs = os.path.abspath(video_path)
            temp_video_abs = os.path.abspath(temp_video)
            
            cmd = f'ffmpeg -y -i "{video_path_abs}" -filter:v "setpts={speed_factor}*PTS" "{temp_video_abs}"'
            Logger.info(f"執行命令: {cmd}")
            
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await process.communicate()
            except Exception as e:
                Logger.error(f"ffmpeg 調整視頻速度進程通信錯誤: {str(e)}")
                # 嘗試終止進程
                try:
                    process.terminate()
                    await asyncio.sleep(2)
                    if process.returncode is None:
                        process.kill()
                except:
                    pass
                raise Exception(f"視頻速度調整失敗 (通信錯誤): {str(e)}")
            
            if process.returncode != 0:
                Logger.error(f"視頻速度調整錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
                raise Exception(f"視頻速度調整失敗: {stderr.decode() if stderr else '未知錯誤'}")
            
            video_path = temp_video
            temp_files.append(temp_video)  # 添加到臨時文件列表
            Logger.info(f"✓ 視頻速度調整完成，速度調整因子: {speed_factor:.2f}")
        
        Logger.info(f"[步驟6] 合併視頻和音頻...")
        final_video = await merge_video_audio(video_path, audio_path, task_id)
        temp_files.append(final_video)  # 添加到臨時文件列表
        
        Logger.info(f"✓ 視頻合併完成，最終文件: {final_video}")
        blob = Config.gcs_generate_bucket.blob(f"{region.lower()}/{client_id}/{task_id}.mp4")
        blob.upload_from_filename(final_video)
        Logger.info(f"✓ 視頻上傳完成，路徑: {blob.public_url}, EndTime: {datetime.now(timezone.utc)}")
        await MongoDB.upsert_one(
            f"{region.title()}Video", 
            {'task_id': task_id}, 
            {
                "$set": {
                    "metadata.animation": animation_script if 'animation_script' in locals() else "",
                    "status": "success",
                    "updated_at": datetime.now(timezone.utc)
                }
            },
            "MEDIA"
        )
    except Exception as e:
        Logger.info(f"視頻生成失敗，準備上傳空白視頻: {str(e)}")
        try:
            # 生成一秒鐘的空白視頻
            blank_video_path = await generate_blank_video(task_id)
            temp_files.append(blank_video_path)  # 添加到臨時文件列表
            
            # 上傳空白視頻到GCS
            blank_blob = Config.gcs_generate_bucket.blob(f"{region.lower()}/{client_id}/{task_id}.mp4")
            blank_blob.upload_from_filename(blank_video_path)
            Logger.info(f"✓ 空白視頻上傳完成，路徑: {blank_blob.public_url}")
            
            await MongoDB.upsert_one(
                f"{region.title()}Video", 
                {'task_id': task_id}, 
                {
                    "$set": {
                        "metadata.animation": animation_script if 'animation_script' in locals() else "",
                        "status": "error",
                        "error": str(e),
                        "fallback_video": True,
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                "MEDIA"
            )
        except Exception as fallback_error:
            Logger.error(f"上傳空白視頻失敗: {str(fallback_error)}")
            await MongoDB.upsert_one(
                f"{region.title()}Video", 
                {'task_id': task_id}, 
                {
                    "$set": {
                        "metadata.animation": animation_script if 'animation_script' in locals() else "",
                        "status": "error",
                        "error": str(e),
                        "fallback_error": str(fallback_error),
                        "updated_at": datetime.now(timezone.utc)
                    }
                },
                "MEDIA"
            )
        raise e
    finally:
        Logger.info(f"[步驟7] 開始清理臨時文件...")
        for file_path in temp_files:
            try:
                if file_path and os.path.exists(file_path):
                    os.remove(file_path)
                    Logger.debug(f"已刪除臨時文件: {file_path}")
            except Exception as e:
                Logger.error(f"刪除臨時文件失敗: {file_path}, 錯誤: {str(e)}")
        for dir_path in temp_dirs:
            try:
                if dir_path and os.path.exists(dir_path):
                    shutil.rmtree(dir_path)
                    Logger.debug(f"已刪除臨時目錄: {dir_path}")
            except Exception as e:
                Logger.error(f"刪除臨時目錄失敗: {dir_path}, 錯誤: {str(e)}")
        try:
            pattern = os.path.join(tempfile.gettempdir(), f"*{task_id}*")
            for temp_file in glob.glob(pattern):
                if os.path.isfile(temp_file):
                    os.remove(temp_file)
                    Logger.debug(f"已刪除其他臨時文件: {temp_file}")
        except Exception as e:
            Logger.error(f"清理其他臨時文件失敗: {str(e)}")
        
        Logger.info(f"✓ 臨時文件清理完成")

async def generate_manim_script(text: str, voice: str, image_base64: str) -> str:
    contentList = [f"使用者提供的內容：{text}, 語音語言：{voice}"]
    response = Config.vertex_client.models.generate_content(
        model=Config.vertex_model, 
        contents=contentList,
        config=types.GenerateContentConfig(temperature=0.0, system_instruction=MANIM_SCRIPT_PROMPT),
    )
    content = response.text.strip()
    start_tag = "<manim_script>"
    end_tag = "</manim_script>"
    start_index = content.find(start_tag)
    end_index = content.find(end_tag)
    if start_index != -1 and end_index != -1:
        content = content[start_index + len(start_tag):end_index].strip()
    if content.endswith("```"):
        content = content.rsplit("```", 1)[0].strip()
    
    # 檢查最後100個字符是否包含```
    last_100_chars = content[-100:] if len(content) > 100 else content
    if "```" in last_100_chars:
        content = content.rsplit("```", 1)[0].strip()
    # 尋找 manim 代碼的開始
    start_index = content.find("from manim import *")
    if start_index != -1:
        content = content[start_index:].strip()    
    return content

async def generate_speech_script(animation_script: str, voice: str) -> str:
    contentList = [f"使用者提供的動畫腳本：{animation_script}, 語音語言：{voice}"]
    response = Config.vertex_client.models.generate_content(
        model=Config.vertex_model, 
        contents=contentList,
        config=types.GenerateContentConfig(temperature=0.0, system_instruction=SPEECH_SCRIPT_PROMPT),
    )
    content = response.text.strip()
    start_tag = "<output>"
    end_tag = "</output>"
    start_index = content.find(start_tag) + len(start_tag)
    end_index = content.find(end_tag)
    
    if start_index != -1 and end_index != -1:
        output_content = content.strip()[start_index:end_index].strip()
        return output_content
    return content

async def generate_video(animation_script: str) -> tuple:
    temp_dir = tempfile.mkdtemp()
    try:
        script_path = os.path.join(temp_dir, "animation_script.py")
        with open(script_path, "w", encoding="utf-8") as f:
            f.write(animation_script)
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        output_name = f"video_{timestamp}"
        output_dir = os.path.join(temp_dir, "output")
        os.makedirs(output_dir, exist_ok=True)
        try:
            scene_name = None
            for line in animation_script.split("\n"):
                if "class" in line and "Scene" in line:
                    parts = line.split("class ")[1].split("(")[0].strip()
                    scene_name = parts
                    break
            if not scene_name:
                raise Exception("無法在腳本中找到場景類")
            Logger.info(f"找到場景類: {scene_name}")
            
            has_gpu = False
            try:
                gpu_check_cmd = "nvidia-smi"
                gpu_process = await asyncio.create_subprocess_shell(
                    gpu_check_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE
                )
                try:
                    gpu_stdout, gpu_stderr = await gpu_process.communicate()
                    has_gpu = gpu_process.returncode == 0
                except Exception as e:
                    Logger.error(f"GPU 檢測通信錯誤: {str(e)}")
                    has_gpu = False
                
                if has_gpu:
                    Logger.info("檢測到 GPU，將使用 GPU 進行渲染")
                else:
                    Logger.info("未檢測到 GPU，將使用 CPU 進行渲染")
            except Exception as e:
                Logger.info(f"GPU 檢測過程中發生錯誤: {str(e)}，將使用 CPU 進行渲染")
            
            # 檢查 xvfb 是否安裝
            has_xvfb = False
            try:
                # 直接檢查檔案是否存在
                xvfb_paths = ["/usr/bin/xvfb-run", "/usr/local/bin/xvfb-run", "/bin/xvfb-run"]
                for path in xvfb_paths:
                    if os.path.exists(path) and os.path.isfile(path):
                        has_xvfb = True
                        Logger.info(f"檢測到 xvfb-run 於路徑: {path}")
                        break
                
                if not has_xvfb:
                    Logger.info("未檢測到 xvfb-run，無法使用虛擬顯示器")
            except Exception as e:
                Logger.info(f"xvfb 檢測過程中發生錯誤: {str(e)}")
            
            # 複製資源目錄到臨時目錄
            original_data_dir = os.path.join(os.getcwd(), "data")
            temp_data_dir = os.path.join(temp_dir, "data")
            if os.path.exists(original_data_dir):
                Logger.info(f"正在複製資源目錄 {original_data_dir} 到臨時目錄 {temp_data_dir}")
                shutil.copytree(original_data_dir, temp_data_dir)
            else:
                Logger.info(f"資源目錄 {original_data_dir} 不存在，跳過複製")
            
            # 根據 GPU 可用性選擇渲染命令
            if has_gpu:
                cmd = f"cd {temp_dir} && CUDA_VISIBLE_DEVICES=0 LIBVA_DRIVER_NAME=nvidia LIBVA_MESSAGING_LEVEL=1 __NV_PRIME_RENDER_OFFLOAD=1 __GLX_VENDOR_LIBRARY_NAME=nvidia xvfb-run -a -e /dev/stderr python -m manim animation_script.py {scene_name} -o {output_name} --media_dir {output_dir} -ql --renderer=opengl --write_to_movie"
            else:
                cmd = f"cd {temp_dir} && python -m manim animation_script.py {scene_name} -o {output_name} --media_dir {output_dir} -ql"
            
            Logger.info(f"執行命令: {cmd}")
            process = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await process.communicate()
            except Exception as e:
                Logger.error(f"Manim 進程通信錯誤: {str(e)}")
                # 嘗試終止進程
                try:
                    process.terminate()
                    await asyncio.sleep(2)
                    if process.returncode is None:
                        process.kill()
                except:
                    pass
                raise Exception(f"Manim 進程通信失敗: {str(e)}")
                
            if process.returncode != 0:
                Logger.error(f"Manim 視頻生成錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
                raise Exception(f"視頻生成失敗: {stderr.decode() if stderr else '未知錯誤'}")
                
            Logger.info(f"Manim 輸出: {stdout.decode() if stdout else '無標準輸出'}")
            if stderr:
                Logger.info(f"Manim 錯誤輸出: {stderr.decode()}")
                
            video_files = []
            for root, _, files in os.walk(output_dir):
                for file in files:
                    if file.endswith(".mp4"):
                        video_files.append(os.path.join(root, file))
                        Logger.debug(f"找到視頻文件: {os.path.join(root, file)}")
            if not video_files:
                raise Exception("找不到生成的視頻文件")
            
            # 確保我們使用主視頻文件，而不是部分視頻文件
            main_video_files = [f for f in video_files if "partial_movie_files" not in f]
            if main_video_files:
                video_path = main_video_files[0]
            else:
                # 如果找不到主視頻，使用第一個部分視頻
                video_path = video_files[0]
            
            # 檢查文件是否存在
            if not os.path.exists(video_path):
                raise FileNotFoundError(f"找不到視頻文件: {video_path}")
            
            cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{video_path}"'
            proc = await asyncio.create_subprocess_shell(
                cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            try:
                stdout, stderr = await proc.communicate()
            except Exception as e:
                Logger.error(f"ffprobe 進程通信錯誤: {str(e)}")
                # 嘗試終止進程
                try:
                    proc.terminate()
                    await asyncio.sleep(2)
                    if proc.returncode is None:
                        proc.kill()
                except:
                    pass
                raise Exception(f"獲取視頻時長失敗 (通信錯誤): {str(e)}")
            
            if proc.returncode != 0:
                Logger.error(f"獲取視頻時長錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
                raise Exception(f"獲取視頻時長失敗: {stderr.decode() if stderr else '未知錯誤'}")
                
            video_duration = float(stdout.decode('utf-8').strip())
            return video_path, video_duration, temp_dir
        except Exception as e:
            Logger.error(f"視頻生成過程中發生錯誤: {str(e)}")
            raise e
    except Exception as e:
        # 如果發生錯誤，確保臨時目錄會被清理
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise e

async def generate_speech(speech_script: str, voice: str, task_id: str) -> tuple:
    try:
        if not speech_script:
            raise ValueError("語音文本不能為空")
        rate = 0
        volume = 0
        rate = max(-100, min(100, rate))
        rate_str = f"{rate:+d}%"  # 例如: "+0%", "+50%", "-20%"
        volume = max(-100, min(100, volume))
        volume_str = f"{volume:+d}%"  # 例如: "+0%", "+50%", "-20%"
        if rate != 0:
            communicate = Communicate(
                text=speech_script, 
                voice=voice,
                rate=rate_str
            )
        else:
            communicate = Communicate(
                text=speech_script, 
                voice=voice
            )
        audio_data = b""
        try:
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    audio_data += chunk["data"]
        except Exception as e:
            Logger.error(f"語音串流處理錯誤: {str(e)}")
            raise ValueError(f"語音串流處理失敗: {str(e)}")
            
        if not audio_data:
            raise ValueError(f"未收到音頻數據，使用的參數：voice={voice}, rate={rate_str}, volume={volume_str}")
        
        temp_audio_path = os.path.join(tempfile.gettempdir(), f"temp_audio_{task_id}.wav")
        with open(temp_audio_path, "wb") as f:
            f.write(audio_data)
        
        # 確保文件存在
        if not os.path.exists(temp_audio_path):
            raise FileNotFoundError(f"語音文件不存在: {temp_audio_path}")
            
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{temp_audio_path}"'
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await proc.communicate()
        except Exception as e:
            Logger.error(f"ffprobe 語音時長進程通信錯誤: {str(e)}")
            # 嘗試終止進程
            try:
                proc.terminate()
                await asyncio.sleep(2)
                if proc.returncode is None:
                    proc.kill()
            except:
                pass
            raise Exception(f"獲取音頻時長失敗 (通信錯誤): {str(e)}")
        
        if proc.returncode != 0:
            Logger.error(f"獲取音頻時長錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
            raise Exception(f"獲取音頻時長失敗: {stderr.decode() if stderr else '未知錯誤'}")
            
        audio_duration = float(stdout.decode('utf-8').strip())
        return temp_audio_path, audio_duration
    except Exception as e:
        Logger.error(f"語音生成過程中發生錯誤: {str(e)}")
        raise e

async def merge_video_audio(video_path: str, audio_path: str, task_id: str) -> str:
    """
    合併視頻和音頻文件
    """
    try:
        # 確保源文件存在
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"視頻文件不存在: {video_path}")
        if not os.path.exists(audio_path):
            raise FileNotFoundError(f"音頻文件不存在: {audio_path}")
            
        output_path = os.path.join(tempfile.gettempdir(), f"final_{task_id}.mp4")
        
        # 使用絕對路徑
        video_path_abs = os.path.abspath(video_path)
        audio_path_abs = os.path.abspath(audio_path)
        output_path_abs = os.path.abspath(output_path)
        
        cmd = f'ffmpeg -y -i "{video_path_abs}" -i "{audio_path_abs}" -c:v copy -c:a aac "{output_path_abs}"'
        Logger.info(f"執行命令: {cmd}")
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await process.communicate()
        except Exception as e:
            Logger.error(f"ffmpeg 合併進程通信錯誤: {str(e)}")
            # 嘗試終止進程
            try:
                process.terminate()
                await asyncio.sleep(2)
                if process.returncode is None:
                    process.kill()
            except:
                pass
            raise Exception(f"視頻合併失敗 (通信錯誤): {str(e)}")
        
        if process.returncode != 0:
            Logger.error(f"視頻合併錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
            raise Exception(f"視頻合併失敗: {stderr.decode() if stderr else '未知錯誤'}")
        
        # 確保輸出文件存在
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"合併後的視頻文件不存在: {output_path}")
            
        return output_path
    except Exception as e:
        Logger.error(f"視頻合併過程中發生錯誤: {str(e)}")
        raise e

async def generate_blank_video(task_id: str) -> str:
    """
    生成一秒鐘的空白視頻
    """
    try:
        output_path = os.path.join(tempfile.gettempdir(), f"blank_{task_id}.mp4")
        
        # 使用ffmpeg生成一秒鐘的空白視頻
        cmd = f'ffmpeg -y -f lavfi -i color=c=white:s=1280x720:d=1 -c:v libx264 -pix_fmt yuv420p "{output_path}"'
        Logger.info(f"執行命令生成空白視頻: {cmd}")
        
        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        try:
            stdout, stderr = await process.communicate()
        except Exception as e:
            Logger.error(f"ffmpeg 空白視頻進程通信錯誤: {str(e)}")
            # 嘗試終止進程
            try:
                process.terminate()
                await asyncio.sleep(2)
                if process.returncode is None:
                    process.kill()
            except:
                pass
            raise Exception(f"空白視頻生成失敗 (通信錯誤): {str(e)}")
        
        if process.returncode != 0:
            Logger.error(f"空白視頻生成錯誤: {stderr.decode() if stderr else '無錯誤輸出'}")
            raise Exception(f"空白視頻生成失敗: {stderr.decode() if stderr else '未知錯誤'}")
        
        # 確保輸出文件存在
        if not os.path.exists(output_path):
            raise FileNotFoundError(f"空白視頻文件不存在: {output_path}")
            
        return output_path
    except Exception as e:
        Logger.error(f"空白視頻生成過程中發生錯誤: {str(e)}")
        raise e

async def generate_animation_story(text: str, voice: str, image_base64: str) -> str:
    contentList = [f"{text}"]
    if image_base64:
        image_data = base64.b64decode(image_base64)
        organ = PIL.Image.open(io.BytesIO(image_data))
        contentList.append(organ)
    response = Config.vertex_client.models.generate_content(
        model=Config.vertex_model, 
        contents=contentList,
        config=types.GenerateContentConfig(
            temperature=0.0, 
            system_instruction="""
            你是一位充滿活力和親和力的台灣K12教育動畫指導老師。
            請以生動活潑、對話式的語言創建教育動畫內容，符合以下要求：
            1) 使用親切的開場白（如「大家好！今天我們要學習...」）並以對話式的口吻引導整個學習過程；
            2) 將教學流程設計為：活潑的開場介紹、簡明易懂的概念解釋、生活化的具體例子、清晰的解題步驟、實用的生活應用，最後是鼓勵性的總結；
            3) 使用學生熟悉的日常用語和比喻，避免生硬的學術語言，加入適當的提問和感嘆詞增加互動感；
            4) 每個概念都搭配生動有趣的例子，例如使用學生熟悉的情境進行演示；
            5) 補充知識在日常生活中的實際應用，讓學生感受到學習的實用性；
            6) 用友善的語氣提醒學生常見的錯誤和解決方法，鼓勵學生積極練習。
            7) 請以內容重點概念為標題（例如：指數的應用）。
            
            請根據使用者提供的內容，生成符合台灣教育體系的動畫腳本，內容應準確、有教育價值、親切易懂且充滿活力。""", 
            tools=[types.Tool(google_search=types.GoogleSearch())]
        ),
    )
    Logger.debug(response.text)
    return response.text

async def check_animation_script(animation_script: str) -> str:
    contentList = [f"{animation_script}"]
    response = Config.vertex_client.models.generate_content(
        model=Config.vertex_model, 
        contents=contentList,
        config=types.GenerateContentConfig(temperature=0.0, system_instruction="""
            你是一位專業的 Manim 動畫腳本審核專家。請檢查並優化提供的 Manim 動畫腳本，確保：
            
            1. 修正所有語法錯誤、邏輯錯誤或運行時可能出現的問題，包括但不限於：
               - 不完整的語句（如只有 self. 而沒有方法調用）
               - 缺少括號、逗號或其他標點符號
               - 不正確的縮進
               - 未完成的代碼行
            2. 確保動畫中只有background_image可以使用 ImageMobject, 其餘的文字和圖形都必須使用 Manim 內建物件
            3. 確保每個場景和畫面都明確應用了適當的背景色或背景圖，保持視覺一致性
            4. 確保所有字幕和文字內容都在視頻範圍內，沒有字幕超出畫面邊界
            5. 確保同時出現的文字元素之間有適當間距，避免重疊或過度擁擠
            6. 確認數學公式的正確性和格式，使用正確的 LaTeX 語法
            7. 檢查動畫轉場效果的流暢性，確保動畫時長合理
            8. 確保腳本中的顏色使用 Manim 支持的格式 (如 WHITE, RED, BLUE_A 等) 或 RGB/十六進制值
            9. 優化代碼結構，移除冗餘代碼，提高執行效率
            10. 確保腳本開頭中包含 'import os' 語句，此為必要導入，必須放在其他導入語句之後
            11. 對於中文內容，必須使用 Text 類來顯示，保持原始的中文文字內容不變
            12. 【重要】對於數學公式，使用 MathTex 類，但絕對禁止包含任何中文字符，包括：
                - 中文單位：公斤、米、秒、度、年、月、日等
                - 中文變量：身高、體重、年齡、速度等
                - 任何中文文字，即使在 \\text{} 內也不允許
            13. 【重要】如果原腳本中有類似 MathTex(r"(100 \\times 身高 - 80) \\times 0.7") 的代碼，必須改為：
                - 數學部分：MathTex(r"(100 \\times h - 80) \\times 0.7") 使用英文變量
                - 說明部分：Text("其中 h 代表身高") 用 Text 類說明變量含義
                - 用 VGroup 組合兩者
            14. 絕對不要翻譯或修改原始腳本中 Text() 內的中文文字內容，必須保持中文文字的原貌
            15. 【強制檢查】掃描所有 MathTex 內容，如發現任何中文字符必須移除或替換為英文變量
            
            重要提醒：請保留所有原始的中文文字內容，不要進行任何翻譯或語言轉換。
            請直接返回修正後的完整腳本，不需要額外解釋。修改時須保留原始腳本的教學目的和核心內容。
            必須確保返回的是可執行的完整 Manim 腳本，包含所有必要的導入語句和類定義。
            
            最終檢查清單：
            - 確保每一行代碼都是完整的語句，沒有被截斷的代碼行
            - 確保所有方法調用都有完整的語法（如 .scale(0.7) 不能寫成 .sca）
            - 確保沒有孤立的 self. 或其他不完整的表達式
            - 確保所有括號都正確配對
            - 【關鍵】確保所有 MathTex 內容都不包含任何中文字符
            - 確保腳本可以通過 Python 語法檢查
        """),
    )
    content = response.text.strip()
    last_100_chars = content[-100:] if len(content) > 100 else content
    if "```" in last_100_chars:
        content = content.rsplit("```", 1)[0].strip()
    # 尋找 manim 代碼的開始
    start_index = content.find("from manim import *")
    if start_index != -1:
        content = content[start_index:].strip() 
    Logger.debug(content)
    return content
    


async def identify_keyword(content: str) -> str:
    """
    辨識關鍵字
    """
    mapping_table = {
        "正數和負數": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749800041.mp4",
        "數線與相對數" : "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749800042.mp4",
        "絕對值" : "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749799905.mp4",
        "有理數的加法": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749799791.mp4",
        "有理數的減法": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749799179.mp4",
        "一元一次方程式": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1750153386.mp4",
        "假設語氣": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749722642.mp4",
        "工業革命": "https://storage.googleapis.com/generate_educational_video/openql/38788/video_38788_1749744118.mp4",
        }
    
    if '絕對值' in content:
        return mapping_table['絕對值']
    elif '數線' in content or "數軸" in content:
        return mapping_table['數線與相對數']
    elif '一元一次方程式' in content:
        return mapping_table['一元一次方程式']
    elif '有理數' in content and '加法' in content:
        return mapping_table['有理數的加法']
    elif '有理數' in content and '減法' in content:
        return mapping_table['有理數的減法']
    elif '正數' in content:
        return mapping_table['正數和負數']
    elif '負數' in content:
        return mapping_table['正數和負數']
    elif '假設語氣' in content:
        return mapping_table['假設語氣']
    elif '工業革命' in content:
        return mapping_table['工業革命']
    else:
        return None
