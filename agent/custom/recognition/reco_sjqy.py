import os
import json
from datetime import datetime

from PIL import Image
from maa.agent.agent_server import AgentServer
from maa.custom_recognition  import CustomRecognition
from maa.context import Context
from fuzzywuzzy import fuzz, process
from typing import Dict, List, Tuple
# from assets.agent.utils.logger import logger
from utils import logger
import time
import re

from .searchAnswer import SearchQuestions

@AgentServer.custom_recognition("reco2")
class reco2_sjqy(CustomRecognition):
    def analyze(
         self,
         context: Context,
         argv: CustomRecognition.AnalyzeArg,
     ) -> CustomRecognition.AnalyzeResult:
        logger.info("进入reco2_sjqy")
        return CustomRecognition.AnalyzeResult(box=(6,134,57,46),detail="福利")



@AgentServer.custom_recognition("reco3")
class reco2_sjqy(CustomRecognition):
    def analyze(
         self,
         context: Context,
         argv: CustomRecognition.AnalyzeArg,
     ) -> CustomRecognition.AnalyzeResult:
        logger.info("进入reco3")

        """
        测试，custom_recognition
        1.识别文字“福利”,box=(6,134,57,46)
        2.发送click
        """
        reco_detail = context.run_recognition(
            "福利",
            argv.image,
            pipeline_override={"福利": {"roi": [6,134,57,46],
                                        "expected":["福利"],
                                        "recognition": "OCR"
                                      }}
            )
        if "福利" in reco_detail.all_results[0].text:
            # 如果找到了"福利"文字，计算中心点并执行点击
            box = reco_detail.box  # 假设box为(x, y, w, h)
            center_x = box[0] + box[2] // 2
            center_y = box[1] + box[3] // 2 

            click_job = context.tasker.controller.post_click(center_x, center_y)
            click_job.wait()  # 等待点击操作完成

        logger.info(reco_detail.all_results[0].text)

        # logger.info(argv.image)
        # print(img)
        # box=(6,134,57,46),detail="福利"
        return CustomRecognition.AnalyzeResult(box=(6,134,57,46),detail="福利")
    


@AgentServer.custom_recognition("sjqy_tiku")
class sjqy_tiku(CustomRecognition):

    def analyze(
         self,
         context: Context,
         argv: CustomRecognition.AnalyzeArg,
     ) -> CustomRecognition.AnalyzeResult:
        logger.info("进入三界奇缘答题agent")

        i = 0
        m= ""
        n = 0
        while i < 30:
            i = i+1
            logger.info(f"第{i}次识别三界奇缘题目")
            #识别三界奇缘题目
            image1 = context.tasker.controller.post_screencap().wait().get()
            reco_detail = context.run_recognition(
                "三界奇缘题目",
                image1,
                
                pipeline_override={"三界奇缘题目": {"roi" : [452,2,655,240],
                                                    "expected":[""],
                                                    "recognition": "OCR"
                                                    }
                                    }
                )
            #识别题目返回值
            # logger.info(reco_detail)
            # 没有识别到题目
            if not reco_detail or not reco_detail.all_results:
                logger.info("没有识别到题目")
                return CustomRecognition.AnalyzeResult(box=(0,0,0,0),detail="未识别到题目")
            
            
            for res in reco_detail.all_results:#识别的结果在题库中搜索问题答案
                text =res.text
                # logger.info(len(text))
                #使用正则去除“第*题”和括号
                pattern = r'第\d+题：|[（(]\d+/\d+[）)]'
                def clean_string(s):
                    return re.sub(pattern, '', s).strip()
                text = clean_string(text)
                excluded_texts = {#排除的文本
                    '第1题：', '第2题：', '第3题：', '第4题：', '第5题：', 
                    '第6题：', '第7题：', '第8题：', '第9题：', '第10题：', 
                    '(1/3)', '(2/3)', '(3/3)', '(1/2)', '(2/2)', '(1/1)',
                    '（1/3）', '（2/3）', '（3/3）', '（1/2）','（2/2）', '（1/1）',
                    '(1/3）', '(2/3）', '(3/3）', '(1/2）', '(2/2）', '(1/1）',
                    '（1/3)', '（2/3)', '（3/3)', '（1/2)','（2/2)', '（1/1)'
                }
                if (text !="" ) and (text not in excluded_texts):   
                    logger.info(f"问题为:"+text)
                    # 在题库中搜索答案
                    # results_value, results_len = fuzzy_search_question_bank(text, question_bank)
                    # logger.info(f"搜索题库返回结果:"+results_value)
                    # logger.info(f"搜索题库返回结果个数:"+str(results_len))
                    
                    #单个问题限制最多次数
                    if n>2:   
                        logger.info(f"多次识别本问题失败，默认点击第一个，失败问题为:"+m)
                        n=0
                        time.sleep(2)
                        context.tasker.controller.post_click(500, 344).wait()
                        time.sleep(1)
                    elif m != text:
                        m = text
                        #查询题库并点击
                        results_value, confidence ,match_type = SearchQuestions(text)
                        
                        if results_value == "未找到匹配的问题":
                            logger.info(f"在不相等中，题库中没有找到答案，问题为:"+text)
                            # 如果题库中没有找到答案，点击第一个答案
                            n = n+1
                            logger.info(f"单次问题失败次数："+str(n))
                            continue
                        new_context = context.clone()
                        image2 = new_context.tasker.controller.post_screencap().wait().get()
                        new_reco_detail = new_context.run_recognition(
                                        "三界奇缘答案位置",
                                        image2,
                                        pipeline_override={"三界奇缘答案位置": {"roi" : [439,218,678,212],
                                                                            "expected":results_value,
                                                                            "recognition": "OCR"
                                                                            }
                                                            }
                                        )
                        # logger.info("new_reco_detail为：{new_reco_detail}")
                        # logger.info(new_reco_detail.box)
                        if new_reco_detail:
                            box = new_reco_detail.box  # 假设box为(x, y, w, h)
                            center_x = box[0] + box[2] // 2
                            center_y = box[1] + box[3] // 2 
                            time.sleep(2)
                            click_job = new_context.tasker.controller.post_click(center_x, center_y)
                            click_job.wait()  # 等待点击操作完成
                            time.sleep(2)
                                # else:
                                #     context.tasker.controller.post_click(500, 344).wait()
                                #     time.sleep(1.5)
                    elif m == text:
                        n = n+1
                        logger.info(f"相同次数为:"+str(n))
                        results_value, confidence ,match_type = SearchQuestions(text)

                        if  results_value == "未找到匹配的问题":
                            logger.info(f"题库中没有找到答案，问题为:"+text)
                            n = n+1
                            logger.info(f"单次问题失败次数"+str(n))
                            continue
                        new_context = context.clone()
                        image2 = new_context.tasker.controller.post_screencap().wait().get()
                        new_reco_detail = new_context.run_recognition(
                                        "三界奇缘答案位置",
                                        image2,
                                        pipeline_override={"三界奇缘答案位置": {"roi" : [439,218,678,212],
                                                                            "expected":results_value,
                                                                            "recognition": "OCR"
                                                                            }
                                                            }
                                        )
                        # logger.info("new_reco_detail为：{new_reco_detail}")
                        # logger.info(new_reco_detail.box)
                        if new_reco_detail:
                            box = new_reco_detail.box  # 假设box为(x, y, w, h)
                            center_x = box[0] + box[2] // 2
                            center_y = box[1] + box[3] // 2 
                            time.sleep(2)
                            click_job = new_context.tasker.controller.post_click(center_x, center_y)
                            click_job.wait()  # 等待点击操作完成
                            time.sleep(2)   
                    
                        
                    

            # logger.info(reco_detail.all_results[0].text)
            # logger.info(reco_detail)
            # return CustomRecognition.AnalyzeResult(box=reco_detail.box,detail="")

@AgentServer.custom_recognition("sjqy_tiku_V2")
class sjqy_tiku_V2(CustomRecognition):

    def analyze(
         self,
         context: Context,
         argv: CustomRecognition.AnalyzeArg,
     ) -> CustomRecognition.AnalyzeResult:
        logger.info("进入三界奇缘答题agent_V2")

        i = 0
        # 未找到答案次数
        NotAnswerCount = 0
        while i < 30:
            i = i+1
            logger.info(f"第{i}次识别三界奇缘题目")
            #识别三界奇缘题目
            image1 = context.tasker.controller.post_screencap().wait().get()
            reco_detail = context.run_recognition(
                "三界奇缘题目",
                image1,
                
                pipeline_override={"三界奇缘题目": {"roi" : [447,40,673,94],
                                                    "expected":[""],
                                                    "recognition": "OCR"
                                                    }
                                    }
                )
            #识别题目返回值
            # logger.info(reco_detail)
            # 没有识别到题目
            if not reco_detail or not reco_detail.all_results:
                # logger.info("没有识别到题目")
                logger.info(f"未在题库中搜索到答案次数:{NotAnswerCount}，请反馈开发者填充题库。")
                return CustomRecognition.AnalyzeResult(box=(0,0,0,0),detail="未识别到题目")
            #整合题目
            ext=''
            for item in reco_detail.all_results:
                if item.text!='':
                    ext+=item.text
            pattern = r'第\d+题：|[（(]\d+/\d+[）)]'
            def clean_string(s):
                return re.sub(pattern, '', s).strip()
            text = clean_string(ext)
            # 获取答案list[]
            results_value, confidence ,match_type = SearchQuestions(text)
            # 如果可信度为零，点击第一个答案
            if confidence == 0:
                # logger.info(f"题库中未找到答案，问题为:{text}.请反馈开发者填充题库")
                NotAnswerCount = NotAnswerCount + 1
                time.sleep(2)
                context.tasker.controller.post_click(500, 344).wait()
                time.sleep(1)
                continue
        
            # 识别答案位置
            new_context = context.clone()
            image2 = new_context.tasker.controller.post_screencap().wait().get()
            new_reco_detail = new_context.run_recognition(
                            "三界奇缘答案位置",
                            image2,
                            pipeline_override={"三界奇缘答案位置": {"roi" : [439,218,678,212],
                                                                "expected":results_value,
                                                                "recognition": "OCR"
                                                                }
                                                }
                            )
            # logger.info("new_reco_detail为：{new_reco_detail}")
            # logger.info(new_reco_detail.box)
            # 点击答案
            if new_reco_detail:
                box = new_reco_detail.box  # 假设box为(x, y, w, h)
                center_x = box[0] + box[2] // 2
                center_y = box[1] + box[3] // 2 
                time.sleep(2)
                click_job = new_context.tasker.controller.post_click(center_x, center_y)
                click_job.wait()  # 等待点击操作完成
                time.sleep(2)

        logger.info(f"未在题库中搜索到答案次数:{NotAnswerCount}，请反馈开发者填充题库。")
        return CustomRecognition.AnalyzeResult(box=(0,0,0,0),detail="答题结束")