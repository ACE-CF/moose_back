import subprocess
import json
import tempfile
import os
# import chardet  解决一下编码问题
from django.http import JsonResponse


def generate_hypothesis1(hypothesis_output_path):
    # 这里的文件名需要后期根据前端id来修改
    try:
        with open(hypothesis_output_path, 'r', encoding='utf-8') as f:
            hypothesis_data = json.load(f)
            print("win!!!")
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': 'Failed to read hypothesis file', 'details': str(e)},
                            status=500)
    return hypothesis_data

def run_details_analysis1(research_question, background_survey, coarse_grained_hypothesis, task_id,api_key,hypothesis_id):
    task_dir = "./tasks/test"
    custom_research_background_and_coarse_hyp_path = os.path.join(task_dir,
                                                                  "custom_research_background_and_coarse_hyp_path.json")
    hierarchical_greedy_path = os.path.join(task_dir, f"hierarchical_greedy_1.pkl")
    display_txt_file_path = os.path.join(task_dir, f"finegrained_hyp_1.txt")
    return display_txt_file_path


# 测试数据函数  ss
def run_custom_background_script1(research_question, background_survey, task_id, api_key):
    task_dir = "./tasks/test"
    evaluation_output_path = os.path.join(task_dir, "evaluation.json")
    print(evaluation_output_path)
    inspiration_output_path = os.path.join(task_dir, "custom_inspiration_corpus.json")
    hypothesis_output_path = os.path.join(task_dir, "hypothesis.json")
    display_output_path = os.path.join(task_dir, "display.txt")

    return task_dir, hypothesis_output_path, inspiration_output_path, display_output_path


# 生成假设函数
def run_custom_background_script(research_question, background_survey, task_id, api_key):
    # 路径准备
    task_dir = f"./tasks/{task_id}"
    os.makedirs(task_dir, exist_ok=True)
    custom_path = os.path.join(task_dir, "question_background.json")

    # 构建命令 step1
    cmd1 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",  # 指向零一项目的虚拟环境
        "E:\\学术\\new\\MOOSE-Chem-dev\\Preprocessing\\custom_research_background_dumping_and_output_displaying.py",
        "--io_type", "0",
        "--research_question", research_question,
        "--background_survey", background_survey,
        "--custom_research_background_path", custom_path
    ]
    # 执行子进程step1
    result = subprocess.run(cmd1, capture_output=True, text=True)
    if result.returncode != 0:
        raise Exception(f"生成自定义研究背景失败: {result.stderr}")

    # 第二步：构建灵感语料
    raw_data_dir = task_dir
    os.makedirs(raw_data_dir, exist_ok=True)  # 确保原始数据目录存在
    inspiration_output_path = os.path.join(task_dir, "custom_inspiration_corpus.json")
    print(inspiration_output_path)
    cmd2 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",
        "E:\\学术\\new\\MOOSE-Chem-dev\\Preprocessing\\construct_custom_inspiration_corpus.py",
        "--raw_data_dir", raw_data_dir,
        "--custom_inspiration_corpus_path", inspiration_output_path
    ]
    result2 = subprocess.run(cmd2, capture_output=True, text=True)
    if result2.returncode != 0:
        raise Exception(f"生成灵感语料失败: {result2.stderr}")

    # 第三步：获取灵感论文
    # 需要修改内容：model_name和base_url这两个怎么填，是要用户填吗，还是默认成什么东西？

    checkpoint_output_path = os.path.join(task_dir, "inspiration.json")
    print(api_key)
    cmd3 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",
        "-u",
        "E:\\学术\\new\\MOOSE-Chem-dev\\Method\\inspiration_screening.py",
        "--model_name", "gpt-4o-mini",
        "--api_type", "0",
        "--api_key", api_key,
        "--base_url", "https://api.claudeshop.top/v1",
        "--chem_annotation_path", "E:\\学术\\new\\MOOSE-Chem-dev\\Data\\chem_research_2024.xlsx",
        "--output_dir", checkpoint_output_path,
        "--corpus_size", "150",
        "--if_use_background_survey", "1",
        "--if_use_strict_survey_question", "1",
        "--num_screening_window_size", "15",
        "--num_screening_keep_size", "3",
        "--num_round_of_screening", "4",
        "--if_save", "1",
        "--background_question_id", "0",
        "--if_select_based_on_similarity", "0",
        "--custom_research_background_path", custom_path,
        "--custom_inspiration_corpus_path", inspiration_output_path
    ]

    # 实时输出另一个项目输出的结果
    # result = subprocess.run(cmd3, capture_output=True, text=True)
    process = subprocess.Popen(
        cmd3,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # 实时打印输出（你也可以改成写日志或 WebSocket 推送）
    for line in process.stdout:
        print(line, end="")

    process.stdout.close()
    return_code = process.wait()
    if result.returncode != 0:
        raise Exception(f"灵感筛选失败: {result.stderr}")

    # step4 灵感假设生成
    hypothesis_output_path = os.path.join(task_dir, "hypothesis.json")

    cmd4 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",
        "-u",
        "E:\\学术\\new\\MOOSE-Chem-dev\\Method\\hypothesis_generation.py",
        "--model_name", "gpt-4o-mini",  # 或其他模型名
        "--api_type", "0",
        "--api_key", api_key,
        "--base_url", "https://api.claudeshop.top/v1",
        "--chem_annotation_path", "E:\\学术\\new\\MOOSE-Chem-dev\\Data\\chem_research_2024.xlsx",
        "--corpus_size", "150",
        "--if_use_strict_survey_question", "1",
        "--if_use_background_survey", "1",
        "--inspiration_dir", checkpoint_output_path,
        "--output_dir", hypothesis_output_path,
        "--if_save", "1",
        "--if_load_from_saved", "0",
        "--if_use_gdth_insp", "0",
        "--idx_round_of_first_step_insp_screening", "2",
        "--num_mutations", "3",
        "--num_itr_self_refine", "3",
        "--num_self_explore_steps_each_line", "3",
        "--num_screening_window_size", "12",
        "--num_screening_keep_size", "3",
        "--if_mutate_inside_same_bkg_insp", "1",
        "--if_mutate_between_diff_insp", "1",
        "--if_self_explore", "0",
        "--if_consider_external_knowledge_feedback_during_second_refinement", "0",
        "--inspiration_ids", "-1",
        "--recom_inspiration_ids",
        "--recom_num_beam_size", "5",
        "--self_explore_inspiration_ids",
        "--self_explore_num_beam_size", "5",
        "--max_inspiration_search_steps", "3",
        "--background_question_id", "0",
        "--custom_research_background_path", custom_path,
        "--custom_inspiration_corpus_path", inspiration_output_path
    ]

    process = subprocess.Popen(
        cmd4,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")  # 或传给前端

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise Exception("生成研究假设失败，子进程异常退出。")

    # step5 假设评估
    evaluation_output_path = os.path.join(task_dir, "evaluation.json")

    cmd5 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",
        "-u",
        "E:\\学术\\new\\MOOSE-Chem-dev\\Method\\evaluate.py",
        "--model_name", "gpt4",  # 或其他模型名
        "--api_type", "1",
        "--api_key", api_key,
        "--base_url", "https://api.claudeshop.top/v1",
        "--chem_annotation_path", "E:\\学术\\new\\MOOSE-Chem-dev\\Data\\chem_research_2024.xlsx",
        "--corpus_size", "150",
        "--hypothesis_dir", hypothesis_output_path,
        "--output_dir", evaluation_output_path,
        "--if_save", "1",
        "--if_load_from_saved", "0",
        "--if_with_gdth_hyp_annotation", "0",
        "--custom_inspiration_corpus_path", inspiration_output_path
    ]

    process = subprocess.Popen(
        cmd5,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")  # 或通过 websocket / yield 发送给前端实时显示

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise Exception("研究假设评估失败，子进程异常退出。")
    # step6 获取形成txt样式的输出，形成排名输出
    display_output_path = os.path.join(task_dir, "display.txt")

    cmd6 = [
        "E:\\学术\\new\\MOOSE-Chem-dev\\venv\\Scripts\\python.exe",
        "-u",
        "E:\\学术\\new\\MOOSE-Chem-dev\\Preprocessing\\custom_research_background_dumping_and_output_displaying.py",
        "--io_type", "1",
        "--research_question", research_question,
        "--background_survey", background_survey,
        "--evaluate_output_dir", evaluation_output_path,
        "--display_dir", display_output_path
    ]
    process = subprocess.Popen(
        cmd6,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    for line in process.stdout:
        print(line, end="")  # 实时打印日志，或发给前端

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise Exception("展示结果生成失败，子进程异常退出。")
    return task_dir, hypothesis_output_path, inspiration_output_path, display_output_path


# 验证API的合理性——还没写
def validate_api_key(api_key):
    # 假设我们有一个固定的 API 密钥，可以根据需要修改
    return api_key


# myapp/utils.py
#处理假设排序的txt函数
def parse_txt_to_ranking_data(txt_file_path):
    ranking_data = []

    try:
        # 目前暂时用ignore来解决，可能不稳定，看情况修改一下后端的部分
        with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
        # with open(txt_file_path, 'rb') as f:
        #     raw_data = f.read()
        #     detected = chardet.detect(raw_data)
        #     encoding = detected['encoding'] or 'utf-8'
        # lines = raw_data.decode(encoding, errors='ignore').splitlines()
        current_item = {}  # 当前正在处理的一个 hypothesis 数据
        current_hypothesis_lines = []  # 当前 hypothesis 的正文内容（可能有多行）

        for line in lines:
            line = line.strip()
            if line.startswith("Hypothesis ID:"):
                if current_item:
                    current_item["Hypothesis A"] = "\n".join(current_hypothesis_lines).strip()
                    ranking_data.append(current_item)
                    current_item = {}
                    current_hypothesis_lines = []

                current_item["Hypothesis ID"] = int(line.split(":")[1].strip())

            elif line.startswith("Averaged Score:"):
                score_str = line.split(":", 1)[1].split(";")[0].strip()
                current_item["Averaged Score"] = float(score_str)

                # current_item["Averaged Score"] = float(line.split(":")[1].strip())

            elif line == "":
                continue

            elif line.startswith("Number of rounds:"):
                continue
            else:
                current_hypothesis_lines.append(line)

        # 加入最后一条
        if current_item:
            current_item["Hypothesis A"] = "\n".join(current_hypothesis_lines).strip()
            ranking_data.append(current_item)

        return ranking_data

    except Exception as e:
        raise RuntimeError(f"Failed to parse txt file: {str(e)}")


# 处理进一步假设的文件
def parse_hypotheses_file(txt_file_path):
    hypotheses_data = []

    try:
        with open(txt_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()

        current_item = {}
        current_content_lines = []

        for line in lines:
            line = line.strip()
            if line.lower().startswith("hypothsis"):
                if current_item:
                    current_item["Hypothesis"] = "\n".join(current_content_lines).strip()
                    hypotheses_data.append(current_item)
                    current_item = {}
                    current_content_lines = []

                # 处理 "Hypothsis 0:" 类行
                parts = line.split()
                hypothesis_id = int(parts[1].replace(":", "").strip())
                current_item["Hypothesis ID"] = hypothesis_id
            else:
                if line:
                    current_content_lines.append(line)

        # 添加最后一个
        if current_item:
            current_item["Hypothesis"] = "\n".join(current_content_lines).strip()
            hypotheses_data.append(current_item)

        return hypotheses_data

    except Exception as e:
        print(f"Error while parsing hypotheses: {e}")
        return []



#进一步假设生成函数
def run_details_analysis(research_question, background_survey, coarse_grained_hypothesis, task_id,api_key,hypothesis_id):
    task_dir = f"./tasks/{task_id}"
    os.makedirs(task_dir, exist_ok=True)
    custom_research_background_and_coarse_hyp_path = os.path.join(task_dir, "custom_research_background_and_coarse_hyp_path.json")
#step1:Set function_mode=5 in main.sh.
    cmd1 = [
        "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\venv\\Scripts\\python.exe",
        "-u", "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\Preprocessing\\custom_research_background_dumping.py",
        "--if_load_from_moosechem_ranking_file", "0",
        "--moosechem_ranking_file_path", "E:\\app\\my_moose\\tasks\\62ff9676-bcb5-4965-84eb-e7e1edd80473\\evaluation.json",
        "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path,
        "--research_question", research_question,
        "--background_survey", background_survey,
        "--coarse_grained_hypothesis", coarse_grained_hypothesis
    ]

    process = subprocess.Popen(
        cmd1,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True
    )

    output_lines = []
    for line in process.stdout:
        print(line, end="")  # 可选：用于调试或日志
        output_lines.append(line)

    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise Exception("custom_research_background_dumping 执行失败")
    # print(custom_research_background_and_coarse_hyp_path)


#step2:function_mode=0
    hierarchical_greedy_path = os.path.join(task_dir, f"hierarchical_greedy_{hypothesis_id}.pkl")

    # hierarchical_greedy_path=os.path.join(task_dir, "hierarchical_greedy_path.pkl")
    cmd2 = [
        "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\venv\\Scripts\\python.exe",
        "-u", "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\Method\\hierarchy_greedy.py",
        "--bkg_id", "0",
        "--api_type", "0",
        "--api_key", api_key,
        "--eval_api_key", api_key,
        "--base_url", "https://api.claudeshop.top/v1",
        "--model_name", "gpt-4o-mini",
        "--eval_model_name", "gpt-4o-mini",
        "--output_dir",hierarchical_greedy_path,
        "--if_save", "1",
        "--max_search_step", "150",
        "--locam_minimum_threshold", "2",
        "--if_feedback", "1",
        "--num_hierarchy", "5",
        "--beam_compare_mode", "0",
        "--beam_size_branching", "3",
        "--num_init_for_EU", "3",
        "--num_recom_trial_for_better_hyp", "2",
        "--if_parallel", "1",
        "--if_multiple_llm", "1",
        "--if_use_vague_cg_hyp_as_input", "1",
        "--if_generate_with_example", "1",
        "--if_use_custom_research_background_and_coarse_hyp", "1",
        "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path
    ]

    # 运行并输出结果,暂时注释掉了，用直接结果代替
    process = subprocess.Popen(cmd2, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output_lines = []
    for line in process.stdout:
        print(line, end="")
        output_lines.append(line)
    process.stdout.close()
    return_code = process.wait()
    if return_code != 0:
        raise RuntimeError(f"调用 hierarchy_greedy.py 失败，错误码：{return_code}")
    display_txt_file_path=os.path.join(task_dir, f"finegrained_hyp_{hypothesis_id}.txt")
    cmd3 = [
        "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\venv\\Scripts\\python.exe",
        "E:\\学术\\new\\MOOSE-Chem-Ch2-main\\Preprocessing\\display_hypothesis.py",
        "--if_hierarchical", "1",
        "--hierarchy_id", "4",
        "--start_bkg_id", "0",
        "--end_bkg_id", "0",
        "--display_txt_file_path", display_txt_file_path,
        "--hypothesis_path", hierarchical_greedy_path
    ]
    # 执行并实时打印输出
    process = subprocess.Popen(cmd3, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    output_lines = []
    for line in process.stdout:
        print(line, end="")
        output_lines.append(line)
    process.stdout.close()
    return_code = process.wait()

    if return_code != 0:
        raise RuntimeError(f"display_hypothesis.py 执行失败，错误码：{return_code}")
    return display_txt_file_path
