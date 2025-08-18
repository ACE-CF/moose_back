from django.shortcuts import render
# myapp/views.py
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.exceptions import ValidationError
from .models import FormData
import time
import uuid
import os
from django.conf import settings
from .utils import run_custom_background_script1, generate_hypothesis1, run_details_analysis, parse_hypotheses_file, \
    parse_txt_to_ranking_data, run_details_analysis1, \
    run_custom_background_script
# 在 views.py 中动态添加路径
import sys
import os

# from functools import wraps
# from django.http import JsonResponse
import traceback

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.path.append(os.path.join(BASE_DIR, 'MOOSE-Demo'))
sys.path.append(os.path.join(BASE_DIR, 'MOOSE-Demo-Copy'))
# sys.path.append(os.path.join(BASE_DIR, 'MOOSE-Demo-New/MOOSE-Demo'))

from MooseDemo import MooseDemo
from Utils.demo_utils import load_MC_gene_hypothesis, obtain_selected_hyp_and_feedback_text, \
    full_custom_MC_start_file_research_background_path, full_custom_MC2_start_file_path, load_MC2_gene_hypothesis
# from demo_utils import load_MC_gene_hypothesis, obtain_selected_hyp_and_feedback_text, \
#     full_custom_MC_start_file_research_background_path, full_custom_MC2_start_file_path,load_MC2_gene_hypothesis
from external.MC2.Method.hierarchy_greedy_utils import HGTree
from django.http import FileResponse, Http404


def download_moose1_tree(request):
    file_path = os.path.join(settings.BASE_DIR, "downloadfile", "tree1.json")
    if not os.path.exists(file_path):
        raise Http404("File not found")
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename="moose1_tree.json")

def download_moose2_tree(request):
    file_path = os.path.join(settings.BASE_DIR, "downloadfile", "tree2.pkl")
    if not os.path.exists(file_path):
        raise Http404("File not found")
    return FileResponse(open(file_path, "rb"), as_attachment=True, filename="moose2_tree.json")

@csrf_exempt
def load_file_tree(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=405)

    file2 = request.FILES.get('file2')  # 接收文件
    MooseVersion = request.POST.get('MOOSE_version')  # 接收下拉框值
    if not file2 or not MooseVersion:
        return JsonResponse({'error': 'Missing file or apiType'}, status=400)

        # 3. 生成唯一任务 ID 和目录
    task_id = str(uuid.uuid4())
    # 这两个怪怪的
    task_dir = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id)
    os.makedirs(task_dir, exist_ok=True)

    # task_id = "test2"
    # job_name选择用随机生成的id来取名了，也可以让用户自己取名
    job_name = task_id
    task_dir = f"./StartFiles/{task_id}"
    # 这个地方真正开始就要放开了
    os.makedirs(task_dir, exist_ok=True)

    # 4. 处理文件,保存上传文件（根据实际需求，进行文件解析或存储）
    file_path = os.path.join(task_dir, file2.name)
        # 处理文件的代码，例如存储或解析
    with open(file_path, 'wb') as f:
        for chunk in file2.chunks():
            f.write(chunk)
    # 处理文件和 apiType ...
    if MooseVersion == "1":
        hypothesis_data = generate_hypothesis1(file_path)
        file_name = os.path.basename(file_path)
    else:
        tree = HGTree.load(file_path)
        hypothesis_data = tree.to_tree_dict()
        file_name = os.path.basename(file_path)
    #这里要完成moose2的结果
    print(file_name)
    return JsonResponse({
        'status': 'success',
        'message': 'Hypothesis load successfully',
        'task_id': task_id,
        'hypothesis': hypothesis_data,
        'file_name': file_name
    })


# 从文件加载树  handleTreeFileChange  与项目代码无关
@csrf_exempt
def load_tree(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            task_id = body.get("task_id", "").strip()
            file_name = body.get("file_name", "").strip()
            checkpoint_root_dir = f"./Checkpoints/{task_id}"
            # task_dir = f"./tasks/{task_id}"
            # os.makedirs(task_dir, exist_ok=True)
            file_path = os.path.join(checkpoint_root_dir, file_name)
            print(file_path)
            hypothesis_data = generate_hypothesis1(file_path)
            request.session['last_hypothesis'] = hypothesis_data
            print("task_id:", task_id)
            # 6. 返回 JSON 响应
            return JsonResponse({
                'status': 'success',
                'message': 'Hypothesis changed successfully',
                'task_id': task_id,
                'hypothesis': hypothesis_data,
                'file_name': file_name
            })
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
    return JsonResponse({"status": "error", "message": "Invalid request method"}, status=405)


# 表单提交假设生成  handleSubmit
@csrf_exempt  # 禁用 CSRF 防护
# @safe_json_response
def analyze(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
    try:
        # 1. 获取表单数据
        question = request.POST.get('question')
        survey = request.POST.get('survey')
        api_key = request.POST.get('apiKey')
        hpy1Id = request.POST.get('hpy1Id')
        modelName = request.POST.get('modelName')
        baseUrl = request.POST.get('baseUrl')
        apiType_name = request.POST.get('apiType')
        file = request.FILES.get('file')  # 获取上传的文件

        print("hpy1Id:", hpy1Id)
        if apiType_name == 'azure':
            apiType = 1
        elif apiType_name == 'gemini':
            apiType = 2
        else:
            apiType = 0

        # 3. 生成唯一任务 ID 和目录
        task_id = str(uuid.uuid4())
        task_dir = os.path.join(settings.MEDIA_ROOT, 'tasks', task_id)
        os.makedirs(task_dir, exist_ok=True)

        # task_id = "test3"
        # job_name选择用随机生成的id来取名了，也可以让用户自己取名
        job_name = task_id
        task_dir = f"./StartFiles/{task_id}"
        # 这个地方真正开始就要放开了
        os.makedirs(task_dir, exist_ok=True)

        # 4. 处理文件,保存上传文件（根据实际需求，进行文件解析或存储）
        if file:
            file_path = os.path.join(task_dir, file.name)
            # 处理文件的代码，例如存储或解析
            # For now, we just save the file to the media directory.
            with open(file_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        # print("apiType:" + str(apiType) + ", api_key:" + api_key + ", baseUrl:" + baseUrl + ", modelName:" + modelName)
        moose = MooseDemo(apiType, api_key, baseUrl, modelName, job_name)  # 初始化 MooseDemo
        moose.write_MC_start_file_research_background(question, survey, hpy1Id)  # 步骤 1：写入研究背景
        # 步骤 2：写入灵感语料
        moose.write_MC_start_file_inspiration_corpus(task_dir, hpy1Id)

        # 步骤 3~5：依次运行 pipeline
        # moose.run_MC([1, 0, 0])  # Inspiration Retrieval
        which_stage = [1, 0, 0]
        moose.run_MC(which_stage, init_id=hpy1Id)
        # moose.run_MC([0, 1, 0])  # Hypothesis Composition
        which_stage = [0, 1, 0]
        moose.run_MC(which_stage, init_id=hpy1Id)
        # moose.run_MC([0, 0, 1])  # Hypothesis Ranking
        which_stage = [0, 0, 1]
        moose.run_MC(which_stage, init_id=hpy1Id)

        # 步骤6：加载假设内容
        # gene_hyp_list = load_MC_gene_hypothesis(job_name, modelName)

        # 加载树的data
        hypothesis_output_path = f"./Checkpoints/{job_name}/hypothesis_generation_{modelName}_0_{hpy1Id}_{job_name}.json"
        hypothesis_data = generate_hypothesis1(hypothesis_output_path)
        file_name = os.path.basename(hypothesis_output_path)
        # 从这里开始是原项目调用内容

        # 5. 模拟处理进度（实际可以通过 WebSockets 或轮询更新进度）
        for i in range(1, 6):
            time.sleep(1)  # 模拟处理时间
            progress = i * 20
            print(f"Processing... {progress}%")
        # ✅ 保存结果到 Session
        request.session['last_hypothesis'] = hypothesis_data
        request.session['task_id'] = task_id
        # 6. 返回 JSON 响应
        return JsonResponse({
            'status': 'success',
            'message': 'Hypothesis generated successfully',
            'task_id': task_id,
            'hypothesis': hypothesis_data,
            'file_name': file_name
        })
    except Exception as e:
        # 打印堆栈方便调试
        traceback.print_exc()
        return JsonResponse({
            'status': 'error',
            'message': str(e)  # 或者自定义提示："API 调用失败，请检查配置"
        }, status=200)  # 返回 200 让前端自己处理

    # return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_last_hypothesis(request):
    hypothesis = request.session.get('last_hypothesis')
    if hypothesis:
        return JsonResponse({'status': 'success', 'hypothesis': hypothesis})
    else:
        return JsonResponse({'status': 'error', 'message': 'No hypothesis found'}, status=404)


@csrf_exempt
def rank_view(request):
    if request.method == 'GET':
        # 1. 获取 task_id 参数
        task_id = request.GET.get('task_id')
        modelName = request.GET.get('modelName')
        hpy1Id = request.GET.get('hpy1Id')
        if not task_id:
            return JsonResponse({'status': 'error', 'message': 'Missing task_id'}, status=400)
        try:
            gene_hyp_list = load_MC_gene_hypothesis(task_id, modelName, hpy1Id)
            ranking_data = []
            for idx, (hypothesis, score, scores_list, num_rounds) in enumerate(gene_hyp_list, start=1):
                ranking_data.append({
                    "Rank": idx,
                    "Hypothesis": hypothesis,
                    "AveragedScore": score,
                    "ScoreList": scores_list,
                    "NumRounds": num_rounds
                })
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'success', 'rankingData': ranking_data})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)


@csrf_exempt
def get_hypothesis_details(request):
    if request.method == "POST":
        try:
            body = json.loads(request.body)
            target_text = body.get("hypothesis_text", "").strip()
            question_text = body.get("question", "").strip()
            task_id = body.get("taskId", "").strip()
            survey = body.get("survey", "").strip()
            api_key = body.get("api_key", "").strip()
            hypothesis_id = str(body.get("hypothesisid", "")).strip()
            # print("question_text:", question_text)

            if not target_text:
                return JsonResponse({"status": "error", "message": "Missing hypothesis_text"}, status=400)
            if not task_id:
                return JsonResponse({"status": "error", "message": "Missing task_id"}, status=400)

            display_txt_file_path = run_details_analysis1(question_text, survey, target_text, task_id, api_key,
                                                          hypothesis_id)
            item = parse_hypotheses_file(display_txt_file_path)
            return JsonResponse({"status": "success", "details": item})
            # return JsonResponse({"status": "error", "message": "Hypothesis not found"}, status=404)

        except json.JSONDecodeError:
            return JsonResponse({"status": "error", "message": "Invalid JSON"}, status=400)

    return JsonResponse({"status": "error", "message": "Only POST allowed"}, status=405)


@csrf_exempt
def get_feedback_moose1(request):
    if request.method == 'POST':
        try:
            api_key = request.POST.get('apiKey')
            modelName = request.POST.get('modelName')
            baseUrl = request.POST.get('baseUrl')
            apiType_name = request.POST.get('apiType')
            job_name = request.POST.get('taskId')
            hpy1Id = request.POST.get('hpy1Id')

            if apiType_name == 'azure':
                apiType = 1
            elif apiType_name == 'gemini':
                apiType = 2
            else:
                apiType = 0

            feedback = request.POST.get('feedback')
            selected_gene_hyp = request.POST.get('hypothesisText')

            if not selected_gene_hyp:
                return JsonResponse({'error': 'Missing hypothesis'}, status=400)

            moose_demo = MooseDemo(apiType, api_key, baseUrl, modelName, job_name)  # 初始化 MooseDemo
            # Step 1: 生成要追加的文本
            feedback_text = obtain_selected_hyp_and_feedback_text(selected_gene_hyp, feedback)
            custom_MC_research_background_path = full_custom_MC_start_file_research_background_path(job_name, 0, 0)
            another_MC_research_background_path = full_custom_MC_start_file_research_background_path(job_name, 0,
                                                                                                     hpy1Id)
            moose_demo.initialize_custom_MC_research_background_with_an_existing_file(
                custom_MC_research_background_path, hpy1Id)
            moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file(
                another_MC_research_background_path, hpy1Id)
            moose_demo.append_new_content_to_background_survey_in_start_file_MC(feedback_text, 0)
            moose_demo.run_MC(init_id=hpy1Id, which_stage=[1, 1, 1])
            hypothesis_output_path = f"./Checkpoints/{job_name}/hypothesis_generation_{modelName}_0_{hpy1Id}_{job_name}.json"
            hypothesis_data = generate_hypothesis1(hypothesis_output_path)
            file_name = os.path.basename(hypothesis_output_path)
            print("文件名：", file_name)

            # return JsonResponse({'message': 'Pipeline executed successfully'})
            return JsonResponse({
                'status': 'success',
                'message': 'Hypothesis generated successfully',
                'task_id': job_name,
                'hypothesis': hypothesis_data,
                'file_name': file_name
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def get_feedback_moose2(request):
    if request.method == 'POST':
        try:
            question = request.POST.get('question')
            survey = request.POST.get('survey')
            api_key = request.POST.get('apiKey')
            modelName = request.POST.get('modelName')
            baseUrl = request.POST.get('baseUrl')
            apiType_name = request.POST.get('apiType')
            job_name = request.POST.get('taskId')
            hpy2Id = request.POST.get('hpy2Id')
            int_hpy2Id = int(hpy2Id)

            if apiType_name == 'azure':
                apiType = 1
            elif apiType_name == 'gemini':
                apiType = 2
            else:
                apiType = 0

            feedback = request.POST.get('feedback')
            selected_gene_hyp = request.POST.get('hypothesisText')

            if not selected_gene_hyp:
                return JsonResponse({'error': 'Missing hypothesis'}, status=400)

            moose_demo = MooseDemo(apiType, api_key, baseUrl, modelName, job_name)  # 初始化 MooseDemo
            # Step 1: 生成要追加的文本
            feedback_text = obtain_selected_hyp_and_feedback_text(selected_gene_hyp, feedback)
            # custom_MC_research_background_path = full_custom_MC_start_file_research_background_path(job_name,0,0)
            # another_MC_research_background_path=full_custom_MC_start_file_research_background_path(job_name,0,hpy2Id)
            # moose_demo.initialize_custom_MC_research_background_with_an_existing_file(custom_MC_research_background_path,hpy2Id)
            # moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file(another_MC_research_background_path,hpy2Id)
            # moose_demo.append_new_content_to_background_survey_in_start_file_MC(feedback_text,0)

            # another_MC2_research_background_path = full_custom_MC2_start_file_path(job_name, 0, hpy2Id)
            # print(another_MC2_research_background_path)
            # moose_demo.initialize_custom_MC2_research_background_and_coarse_hyp_with_an_existing_file(
            #     another_MC2_research_background_path, hpy2Id)
            # if int_hpy2Id == 1:
            moose_demo.write_MC2_start_file(question, survey, selected_gene_hyp,
                                            init_hyp_id=hpy2Id)
            moose_demo.append_new_content_to_background_survey_in_start_file_MC2(feedback_text, init_hyp_id=hpy2Id)
            moose_demo.run_MC2(init_hyp_id=hpy2Id)
            num_hierarchy = 5
            bkg_id = 0
            if_hierarchical = 1
            locam_minimum_threshold = 2
            if_feedback = 1
            num_recom_trial_for_better_hyp = 2
            beam_compare_mode = 0
            beam_size_branching = 2
            num_init_for_EU = 3
            if_multiple_llm = 1
            if_use_vague_cg_hyp_as_input = 1
            # hierarchy_id = 4
            # print("---------------------------------------ready1")
            hypothesis_path = f"./Checkpoints/{job_name}/hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_{modelName}_{modelName}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_bkgid_{bkg_id}_init_hyp_id_{hpy2Id}_{job_name}.pkl"
            tree = HGTree.load(hypothesis_path)
            tree_json = tree.to_tree_dict()
            # gene_hyp_list = load_MC2_gene_hypothesis(job_name, model_name=modelName, eval_model_name=modelName,
            #                                                init_hyp_id=hpy2Id)

            file_name = os.path.basename(hypothesis_path)
            print("选择文件名字：", file_name)
            return JsonResponse({
                'status': 'success',
                'message': 'Hypothesis2 generated successfully',
                'hypothesis': tree_json,
                'file_name': file_name
            })
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
    else:
        return JsonResponse({'error': 'Only POST method allowed'}, status=405)


@csrf_exempt
def get_tree2_view(request):
    tree_file_path = os.path.join("data", "saved_tree.pkl")  # 替换为你的路径
    try:
        tree = HGTree.load(tree_file_path)
        tree_json = tree.to_tree_dict()
        return JsonResponse(tree_json, safe=False)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@csrf_exempt
def rank_view2(request):
    if request.method == 'GET':
        # 1. 获取 task_id 参数
        task_id = request.GET.get('task_id')
        modelName = request.GET.get('modelName')
        hpy2Id = request.GET.get('hpy2Id')
        if not task_id:
            return JsonResponse({'status': 'error', 'message': 'Missing task_id'}, status=400)
        try:
            gene_hyp_list = load_MC2_gene_hypothesis(task_id, model_name=modelName, eval_model_name=modelName,
                                                     init_hyp_id=hpy2Id)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

        return JsonResponse({'status': 'success', 'rankingData': gene_hyp_list})

    return JsonResponse({'status': 'error', 'message': 'Invalid request method'}, status=405)
