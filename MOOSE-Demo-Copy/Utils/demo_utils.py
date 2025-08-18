import os, sys, re, json, subprocess
import numpy as np
from openai import OpenAI, AzureOpenAI
from google import genai
from google.genai import types
from .run_MC_MC2 import run_MC, run_MC2
from external.MC.Preprocessing.construct_custom_inspiration_corpus import load_title_abstract
from external.MC2.Method.utils import load_chem_annotation, llm_generation_while_loop, exchange_order_in_list
from external.MC2.Evaluation.analysis import load_final_hypothesis_from_HGTree, load_final_hypothesis_from_json
from external.MC2.Evaluation.evaluate import Evaluator
from external.MC2.Evaluation.analysis import evaluate_hyp


# FUNCTION:
#   Write the research question and background survey to custom_research_background_path; 
def write_MC_start_file_research_background(research_question, background_survey, custom_research_background_path):
    # Save the research question and background survey to a JSON file
    with open(custom_research_background_path, "w") as f:
        json.dump([research_question.strip(), background_survey.strip()], f, indent=4)
    print("Custom research background (for MC) saved to ", custom_research_background_path)

    
# FUNCTION:
#   load title and abstract from raw_insp_xlsx_dir (stores the xls and xlsx files from web of science) and save to custom_inspiration_corpus_path
def write_MC_start_file_inspiration_corpus(raw_insp_xlsx_dir, custom_inspiration_corpus_path):
    # Load title and abstract from raw_insp_xlsx_dir and save to custom_inspiration_corpus_path 
    load_title_abstract(raw_insp_xlsx_dir, custom_inspiration_corpus_path)
    print("Custom inspiration corpus (for MC) saved to ", custom_inspiration_corpus_path)



# Write the research question, background survey, and coarse-grained hypothesis to custom_research_background_and_coarse_hyp_path
def write_MC2_start_file(research_question, background_survey, coarse_grained_hypothesis, custom_research_background_and_coarse_hyp_path):
    # Save the research question and background survey to a JSON file
    with open(custom_research_background_and_coarse_hyp_path, "w") as f:
        json.dump([[research_question.strip(), background_survey.strip(), coarse_grained_hypothesis.strip()]], f, indent=4)
    print("Research background and coarse-grained hypothesis saved to", custom_research_background_and_coarse_hyp_path)


def full_custom_MC_start_file_research_background_path(job_name, bkg_id, init_id):
    return f"./StartFiles/{job_name}/{job_name}_bkg_id_{bkg_id}_init_id_{init_id}_custom_MC_research_background.json"

def full_custom_MC_start_file_inspiration_corpus_path(job_name, bkg_id, init_id):
    return f"./StartFiles/{job_name}/{job_name}_bkg_id_{bkg_id}_init_id_{init_id}_custom_MC_inspiration_corpus.json"


def full_custom_MC2_start_file_path(job_name, bkg_id, init_hyp_id):
    return f"./StartFiles/{job_name}/{job_name}_bkg_id_{bkg_id}_init_hyp_id_{init_hyp_id}_custom_MC2_research_background_and_coarse_hyp.json" 


# load the research question and background survey from the start file of a specific MC job
def load_MC_start_file_research_background(job_name, bkg_id=0, init_id=0):
    # Load the JSON file
    start_file_path = full_custom_MC_start_file_research_background_path(job_name, bkg_id, init_id)
    with open(start_file_path, "r") as f:
        research_question, background_survey = json.load(f)
    return research_question, background_survey


# load the research question, background survey, and coarse-grained hypothesis from the start file of a specific MC2 job
def load_MC2_start_file_research_background_and_coarse_hyp(job_name, bkg_id=0, init_hyp_id=0):
    # Load the JSON file
    start_file_path = full_custom_MC2_start_file_path(job_name, bkg_id, init_hyp_id)
    with open(start_file_path, "r") as f:
        data = json.load(f)
        assert len(data) == 1, "The start file should only contain one element."
        research_question, background_survey, coarse_grained_hypothesis = data[0]
    return research_question, background_survey, coarse_grained_hypothesis



# # which_stage: [0/1, 0/1, 0/1] representing whether perform [inspiration retrieval, hypothesis composition, hypothesis ranking] respectively
# # if_eval_with_gdth_hyp: 0/1, whether to evaluate the hypotheses with groundtruth hypothesis annotation (by default, only the research question in the TOMATO-Chem benchmark has the groundtruth hypothesis annotation); only used when which_stage[2] is 1
# # run the ./MC.sh file
# def run_MC(api_type, api_key, base_url, model_name_insp_retrieval, model_name_gene, model_name_eval, custom_research_background_path, custom_inspiration_corpus_path, which_stage, bkg_id, output_dir_postfix, if_eval_with_gdth_hyp, init_id, if_mutate_inside_same_bkg_insp, if_mutate_between_diff_insp, baseline_type):
#     assert len(which_stage) == 3, "which_stage must be a list of 3 elements."
#     assert all(x in [0, 1] for x in which_stage), "which_stage must contain only 0 or 1."

#     # Prepare the command to run the MC script
#     command = ["./MC.sh", api_type, api_key, base_url, model_name_insp_retrieval, model_name_gene, model_name_eval, custom_research_background_path, custom_inspiration_corpus_path, which_stage[0], which_stage[1], which_stage[2], bkg_id, output_dir_postfix, if_eval_with_gdth_hyp, init_id, if_mutate_inside_same_bkg_insp, if_mutate_between_diff_insp, baseline_type]
#     command = [str(x) for x in command]  # Convert all elements to string
#     print("Running command:", ' '.join(command))
#     # Run the command
#     process = subprocess.Popen(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True,
#         bufsize=1
#     )

#     for line in process.stdout:
#         print(line, end='')  # print each line as it arrives

#     process.wait()  # Wait for the process to finish



# # run the ./MC2.sh file
# def run_MC2(api_type, api_key, base_url, model_name_gene, model_name_eval, custom_research_background_and_coarse_hyp_path, bkg_id, output_dir_postfix, init_hyp_id):
#     # Prepare the command to run the MC2 script
#     command = ["./MC2.sh", api_type, api_key, base_url, model_name_gene, model_name_eval, custom_research_background_and_coarse_hyp_path, bkg_id, output_dir_postfix, init_hyp_id]
#     command = [str(x) for x in command]  # Convert all elements to string
#     print("Running command:", ' '.join(command))
    
#     # Run the command
#     process = subprocess.Popen(
#         command,
#         stdout=subprocess.PIPE,
#         stderr=subprocess.STDOUT,
#         text=True,
#         bufsize=1
#     )

#     for line in process.stdout:
#         print(line, end='')  # print each line as it arrives

#     process.wait()  # Wait for the process to finish
    


# INPUT:
#   eval_file_path: the output_dir of evaluate.py of MC
#   model_name: model name for the output_dir in evaluate.py of MC
# OUTPUT:
#   gene_hyp_list: [[hypothesis, score, scores_list, num_rounds], ...]
def load_MC_gene_hypothesis(output_dir_postfix, model_name, bkg_id=0, init_id=0, if_with_gdth_hyp_annotation=0):
    # Load the JSON file
    eval_file_path = f"./Checkpoints/{output_dir_postfix}/evaluation_{if_with_gdth_hyp_annotation}_{model_name}_{bkg_id}_{init_id}_{output_dir_postfix}.json"
    with open(eval_file_path, "r") as f:
        data = json.load(f)

    research_question = list(data[0].keys())[0]
    # gene_hyp_list: [[hypothesis, score, scores_list, num_rounds], ...]
    gene_hyp_list = []
    for cur_id in range(len(data[0][research_question])):
        cur_hypothesis = data[0][research_question][cur_id][0]
        cur_score = data[0][research_question][cur_id][1]
        cur_scores_list = data[0][research_question][cur_id][2]
        cur_num_rounds = data[0][research_question][cur_id][4]
        gene_hyp_list.append([cur_hypothesis, cur_score, cur_scores_list, cur_num_rounds])
    return gene_hyp_list



# INPUT:
#   output_dir_postfix: job_name
# OUTPUT:
#   gene_hyp_list: [hyp, ...]
#   matched_score_list: [score, ...]
def load_MC_matched_scores(output_dir_postfix, model_name, bkg_id=0, init_id=0, if_with_gdth_hyp_annotation=1):
    assert if_with_gdth_hyp_annotation == 1, "if_with_gdth_hyp_annotation must be 1."
    # Load the JSON file
    eval_file_path = f"./Checkpoints/{output_dir_postfix}/evaluation_{if_with_gdth_hyp_annotation}_{model_name}_{bkg_id}_{init_id}_{output_dir_postfix}.json"
    with open(eval_file_path, "r") as f:
        data = json.load(f)

    research_question = list(data[1].keys())
    assert len(research_question) == 1
    research_question = research_question[0]
    # ranked_hypothesis_collection_with_matched_score: {backgroud_question: ranked_hypothesis_matched_score, ...}
    #   ranked_hypothesis_matched_score: [[hyp, ave_score, scores, core_insp_title, round_id, [first_round_mutation_id, second_round_mutation_id], [matched_score, matched_score_reason]], ...] (here core_insp_title is the matched groundtruth inspiration paper title) (sorted by average score, in descending order)
    ranked_hypothesis_collection_with_matched_score = data[1]

    gene_hyp_list, matched_score_list = [], []
    for cur_id in range(len(data[1][research_question])):
        cur_hyp = data[1][research_question][cur_id][0]
        cur_matched_score = data[1][research_question][cur_id][6][0]
        gene_hyp_list.append(cur_hyp)
        matched_score_list.append(cur_matched_score)
    return gene_hyp_list, matched_score_list


# for both MC and MC2
# which_experiment: 'MC' or 'MC2' (the output format of the final_hypothesis is different)
def load_best_recall_hypothesis_from_ckpt(job_name, cur_id, model_name, model_name_eval, which_experiment):
    assert which_experiment in ['MC', 'MC2'], f"which_experiment must be 'MC' or 'MC2': {which_experiment}"
    # evaluate with ground truth hypothesis annotation
    result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{model_name}_eval_model_name_{model_name_eval}.json"
    with open(result_file_name_eval_with_gdth_hyp, "r") as f:
        data = json.load(f)

    # final_hypothesis: [[hypothesis, score, scores_list, num_rounds], ...] (MC's output); [hyp0, hyp1, ...] (MC2's output)
    final_hypothesis = data[0]
    # final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]; list of lists
    final_scores = data[1]
    # final_scores is a top subset of final_hypothesis (final_hypothesis ranked by self-provided scores without reference, and then pick the top-k (10) hypotheses to evaluate with reference, obtaining the final_scores)
    assert len(final_hypothesis) >= len(final_scores)
    # find the hypothesis with the highest weighted_recall
    best_id = np.argmax([score[4] for score in final_scores])
    if which_experiment == 'MC':
        best_recall_hypothesis = final_hypothesis[best_id][0]
    elif which_experiment == 'MC2':
        best_recall_hypothesis = final_hypothesis[best_id]
    else:
        raise NotImplementedError(which_experiment)
    best_recall_score = final_scores[best_id][4]
    return best_recall_hypothesis, best_recall_score




# INPUT:
#   model_name: used for MC2's inference
#   eval_model_name: used for pairwise evaluation during MC2's inference
# OUTPUT:
#   cur_bkg_hypothesis: [hyp]
def load_MC2_gene_hypothesis(output_dir_postfix, model_name, eval_model_name, init_hyp_id, bkg_id=0, if_hierarchical=1, locam_minimum_threshold=2, if_feedback=1, num_recom_trial_for_better_hyp=2, beam_compare_mode=0, beam_size_branching=2, num_init_for_EU=3, if_multiple_llm=1, if_use_vague_cg_hyp_as_input=1, hierarchy_id=4):

    # cur_bkg_hypothesis: [hyp]
    if if_hierarchical == 1:
        num_hierarchy = 5
        hypothesis_path = f"./Checkpoints/{output_dir_postfix}/hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_{model_name}_{eval_model_name}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_bkgid_{bkg_id}_init_hyp_id_{init_hyp_id}_{output_dir_postfix}.pkl"
        cur_bkg_hypothesis = load_final_hypothesis_from_HGTree(hypothesis_path, hierarchy_id)
    else:
        hypothesis_path = f"./Checkpoints/{output_dir_postfix}/greedy_{locam_minimum_threshold}_{if_feedback}_{model_name}_{eval_model_name}_if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_bkgid_{bkg_id}_init_hyp_id_{init_hyp_id}_{output_dir_postfix}.json"
        cur_bkg_hypothesis = load_final_hypothesis_from_json(hypothesis_path)
        
    return cur_bkg_hypothesis



# Input: 
#   final_hypothesis: [hyp0, hyp1, ...]
#   bkg_id: the id of research question in TOMATO-Chem benchmark, used to retrieve the groundtruth hyp to compare
# Output:
#   final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]
#       len(final_scores) == len(final_hypothesis)
def evaluate_MC2_hyp_with_gdth_reference(api_type, api_key, base_url, model_name, chem_annotation_path, preprocess_groundtruth_components_dir, hyp_type, num_compare_times, final_hypothesis, bkg_id):
    evaluator = Evaluator(model_name, api_type, api_key, base_url, chem_annotation_path, preprocess_groundtruth_components_dir)

    final_scores = evaluate_hyp(final_hypothesis, bkg_id, evaluator, hyp_type, num_compare_times)
    return final_scores






# INPUT
#   keyword_raw_string: eg, "insp1/2: The Hofmeister series; insp3: directional freezing (ref id: 23)"
# OUTPUT
#   insp_list: eg, ['The Hofmeister series', 'directional freezing']
#   insp_prompt: a text prompt summarizing the inspirations
#       eg, "Here are some inspirations we are considering composing the hypothesis with: The Hofmeister series, and directional freezing."
def gdth_insp_keyword_to_text(keyword_raw_string):
    keywords = keyword_raw_string.strip().split(';')
    for cur_id, cur_k in enumerate(keywords):
        # get rid of (ref id: xxx)
        cur_k = re.sub(r'\(ref id: .*?\)', '', cur_k).strip()
        cur_k = re.sub(r'\(ref id .*?\)', '', cur_k).strip()
        # get rid of 'insp1/2', 'insp1', 'insp1/2/3':
        cur_k = re.sub(r'insp\d+(/\d+)*: ', '', cur_k).strip()
        cur_k = re.sub(r'insp \d+(/\d+)*: ', '', cur_k).strip()
        keywords[cur_id] = cur_k
    insp_list = [k for k in keywords if k]
    insp_list = list(set(insp_list))  # remove duplicates

    if len(insp_list) == 0:
        raise Exception("Warning: No inspirations found in the keyword string.")
    
    insp_prompt = "\nHere are some hints we can consider when proposing the hypothesis: " + ', and '.join(insp_list) + '.'
    # return insp_list, insp_prompt
    return insp_prompt


def obtain_selected_hyp_and_feedback_text(selected_hyp, feedback):
    prompts = demo_instruction_prompts("obtain_selected_hyp_and_feedback_text")
    assert len(prompts) == 2, "prompts should have 2 elements."
    full_prompt = prompts[0] + selected_hyp + prompts[1] + feedback
    return full_prompt



# FUNCTION:
#   Provide feedback on a gene hypothesis based on a question and a reference hypothesis.
# INPUT:
#   feedback_strength_level: 0, 1, 2
#       0: soft feedback, only provide vague hints
#       1: stronger feedback, provide more specific hints
#       2: strongest feedback, provide the exact ground truth hypothesis
# OUTPUT:
#   feedback: text
def provide_feedback(question, gdth_hyp, gene_hyp, api_type, api_key, base_url, model_name, feedback_strength_level):
    assert feedback_strength_level in [0, 1, 2], "feedback_strength_level must be 0, 1, or 2."

    # Set API client
    # openai client
    if api_type == 0:
        client = OpenAI(api_key=api_key, base_url=base_url)
    # azure client
    elif api_type == 1:
        client = AzureOpenAI(
            azure_endpoint = base_url, 
            api_key=api_key,  
            api_version="2024-06-01"
        )
    else:
        raise NotImplementedError
    

    if feedback_strength_level == 0:
        prompts = demo_instruction_prompts("feedback_with_reference_v1")
    elif feedback_strength_level == 1:
        prompts = demo_instruction_prompts("feedback_with_reference_v2")
    elif feedback_strength_level == 2:
        prompts = demo_instruction_prompts("feedback_with_reference_v3")
    else:
        raise NotImplementedError

    assert len(prompts) == 4
    full_prompt = prompts[0] + question + prompts[1] + gdth_hyp + prompts[2] + gene_hyp + prompts[3]

    # structured_gene: [[feedback, reason]]
    structured_gene = llm_generation_while_loop(full_prompt, model_name, client, if_structured_generation=True, template=['Reasoning Process:', 'Improvement Feedback:'], temperature=1.0)
    structured_gene = exchange_order_in_list(structured_gene)

    return structured_gene[0][0]



# test whether the api is good
def initialize_client(api_type, api_key, base_url):
    ## initialize client
    # openai client
    if api_type == 0:
        client = OpenAI(api_key=api_key, base_url=base_url)
    # azure client
    elif api_type == 1:
        client = AzureOpenAI(
            azure_endpoint = base_url, 
            api_key=api_key,  
            api_version="2024-06-01"
        )
    # google client
    elif api_type == 2:
        client = genai.Client(api_key=api_key)
    else:
        raise NotImplementedError(f"api_type {api_type} is not supported")
    return client


# test whether the api is good
def test_api(api_type, api_key, base_url, model_name, prompt):
    assert api_type in [0, 1, 2], "api_type must be 0, 1, or 2"
    client = initialize_client(api_type, api_key, base_url)
    
    ## test api
    if api_type in [0, 1]:
        completion = client.chat.completions.create(
        model=model_name,
        temperature=0,
        max_tokens=1000,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
            ]
        )
        generation = completion.choices[0].message.content.strip()
    # google client
    elif api_type == 2:
        response = client.models.generate_content(
            model=model_name, 
            contents=prompt,
            config=types.GenerateContentConfig(
                thinking_config=types.ThinkingConfig(thinking_budget=0)
            )
        )
        generation = response.text.strip()
    return generation


# test whether the api is good
def test_whether_api_is_good(api_type, api_key, base_url, model_name):
    if_good_api = False
    try:
        prompt = "What is the capital of France?"
        generation = test_api(api_type, api_key, base_url, model_name, prompt)
        print(generation)
        if_good_api = True
        print("The api is good.")
    except Exception as e:
        raise Exception(f"The api is not good: {e}")
    return if_good_api



# stores prompts
def demo_instruction_prompts(module_name):
    # very soft feedback
    if module_name == "feedback_with_reference_v1":
        prompts = ['''
                    You are a professor mentoring a PhD student in scientific discovery. You know a specific target hypothesis (the “ground truth”) but must **never reveal it explicitly**—not even key ingredients, materials, or mechanisms.

                    Your role is to guide the student through thoughtful feedback, using probing questions, indirect hints, and constructive critique. Given a research question, the student proposes a hypothesis. Your feedback should emulate a real scientific advisor:

                    - Raise critical questions,
                    - Identify vague logic or unsupported assumptions,
                    - Highlight missing reasoning or overlooked trade-offs,
                    - Suggest general directions or frameworks to explore.

                    You may subtly steer the student by drawing attention to underdeveloped parts of their idea—but keep all hints **abstract and conceptual**. Avoid naming specific methods, materials, or novel ideas from the ground truth.

                    If the student's hypothesis partially overlaps with the ground truth, you may encourage the direction **generically** but must not confirm correctness. Do not praise or validate until the core hypothesis is independently recovered.
                    ''',
                    "\nThe ground truth hypothesis you have in mind is: ",
                    "\nThe student proposes a hypothesis as: ",
                    "\nPlease provide feedback on the student's proposed hypothesis, considering the ground truth hypothesis. Your feedback should be constructive and guide the student towards refining their hypothesis. (response format: 'Reasoning Process: \nImprovement Feedback: \n')"]
    # a bit stronger feedback that might suggest the general direction of the ground truth (but not the exact hypothesis)
    elif module_name == "feedback_with_reference_v2":
        prompts = ['''
                    You are a professor advising a PhD student on scientific hypothesis development. You already know the correct, ground truth hypothesis, but you must not reveal it verbatim. However, in this setting, you **may provide stronger directional guidance** toward the ground truth, as long as you do not quote it or list its exact components.

                    Your task is to give realistic, technically insightful, and constructive feedback on the student's proposed hypothesis, using your knowledge of the ground truth to nudge them toward it. Your feedback should simulate how an experienced scientist might react—analytical, critical, and strategically directive:

                    - Identify key scientific flaws, inconsistencies, or vague logic;
                    - Highlight important mechanisms, material behaviors, or design principles that the student has overlooked;
                    - If the student's hypothesis is off-track, you may **suggest a more promising class of materials, strategy, or concept** that aligns more with the ground truth (but do not directly describe the exact hypothesis);
                    - If the student's hypothesis is partially correct, you may **encourage that direction** and suggest what is missing or needs to be rethought;
                    - Your feedback can include reasoning about why their approach might fail, and what kind of physical or chemical constraints must be respected.

                    **Avoid disclosing the exact hypothesis. Instead, give feedback that helps them get closer while maintaining the spirit of self-discovery.**
                    ''',
                    "\nGround truth hypothesis:\n",
                    "\nStudent's proposed hypothesis:\n",
                    "\nNow provide your feedback based on the instructions above. (response format: 'Reasoning Process: \nImprovement Feedback: \n')"]
    elif module_name == "feedback_with_reference_v3":
        prompts = ['''
                    You are a professor advising a PhD student on scientific hypothesis development. You already know the correct, ground truth hypothesis, but you must not reveal it verbatim. However, in this setting, you **may provide stronger directional guidance** toward the ground truth, as long as you do not quote it or list its exact components.

                    Your task is to give realistic, technically insightful, and constructive feedback on the student's proposed hypothesis, using your knowledge of the ground truth to nudge them toward it. Your feedback should simulate how an experienced scientist might react—analytical, critical, and strategically directive:

                    * Identify key scientific flaws, inconsistencies, or vague logic;
                    * Highlight important mechanisms, material behaviors, or design principles that the student has overlooked;
                    * If the student's hypothesis is off-track, you may **suggest a more promising class of materials, strategy, or concept** that aligns more with the ground truth (but do not directly describe the exact hypothesis);
                    * If the student's hypothesis is partially correct, you may **encourage that direction** and suggest what is missing or needs to be rethought;
                    * Your feedback can include reasoning about why their approach might fail, and what kind of physical or chemical constraints must be respected;
                    * In addition, you may explicitly mention **exactly one missing key concept or chemical** from the ground truth hypothesis to guide the student more clearly.

                    **Avoid disclosing the exact hypothesis beyond the one explicitly allowed concept or chemical. Instead, give feedback that helps them get closer while maintaining the spirit of self-discovery.**
                    ''',
                    "\nGround truth hypothesis:\n",
                    "\nStudent's proposed hypothesis:\n",
                    "\nNow provide your feedback based on the instructions above. (response format: 'Reasoning Process: \nImprovement Feedback: \n')"]

    # not prompt, just to compose information to append to the background survey (as start file)
    elif module_name == "obtain_selected_hyp_and_feedback_text":
        prompts = ["A PhD student has proposed a hypothesis for the research question before, and a senior researcher has provided feedback on the PhD's hypothesis. You may refer to the feedback to better conduct your current task.\nThe PhD's hypothesis is: ",
                "\nThe feedback from the senior researcher for the student proposed hypothesis is:\n"]
    else:
        raise Exception(f"Module {module_name} not recognized.")
    return prompts
