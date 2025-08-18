import json
import glob
import numpy as np
from external.MC2.Evaluation.analysis import load_final_hypothesis_from_HGTree_with_reasoning_steps

def load_result_single_bkg(result_file_name_eval_with_gdth_hyp):
    # collect result files
    with open(result_file_name_eval_with_gdth_hyp, "r") as f:
        data = json.load(f)
    final_hypothesis = data[0]
    final_scores = data[1]
    return final_hypothesis, final_scores


def summarize_result(job_name, model_name, model_name_eval):
    # find all file name start with 'Result_', and then load the result
    all_files = glob.glob(f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_*_model_name_{model_name}_eval_model_name_{model_name_eval}.json")
    result_files = [f for f in all_files if "_bkg_id_7_" not in f]
    result_files.sort()
    print(f"Found {len(result_files)} result files.")
    # stores the weighted_recall scores
    collected_recall_scores = []
    for result_file in result_files:
        # final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]; list of lists
        final_hypothesis, final_scores = load_result_single_bkg(result_file)
        print(f"Loading result from {result_file}...")
        for cur_id in range(len(final_scores)):
            collected_recall_scores.append(final_scores[cur_id][4])
    # calculate the mean and std of the collected recall scores
    print(f"Collected {len(collected_recall_scores)} recall scores.")
    mean_recall_score = np.mean(collected_recall_scores)
    std_recall_score = np.std(collected_recall_scores)
    return mean_recall_score, std_recall_score



# exp_type: MC, MC2
# which_num: 0: precision, 1: recall, 2: f1, 3: weighted_precision, 4: weighted_recall, 5: weighted_f1
def summarize_result_with_reasoning_steps(job_name, model_name, model_name_eval, start_id, end_id, exp_type, which_num):
    assert exp_type in ["MC", "MC2"], "exp_type must be MC or MC2"
    # parameters for the finegrained hypothesis checkpoint file
    num_hierarchy = 5
    locam_minimum_threshold = 2
    if_feedback = 1
    num_recom_trial_for_better_hyp = 2
    beam_compare_mode = 0
    beam_size_branching = 2
    num_init_for_EU = 3
    init_hyp_id = 0
    if_multiple_llm = 1
    if_use_vague_cg_hyp_as_input = 1
    hierarchy_id = 4
    # stores the weighted_recall scores
    collected_recall_scores = []
    collected_ttl_search_steps = []
    for cur_bkg_id in range(start_id, end_id + 1):
        if cur_bkg_id == 7:
            continue
        # load the result file
        cur_result_file_path = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_bkg_id}_model_name_{model_name}_eval_model_name_{model_name_eval}.json"
        # final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]; list of lists
        final_hypothesis, final_scores = load_result_single_bkg(cur_result_file_path)
        print(f"Loading result from {cur_result_file_path}...")
        for cur_id in range(len(final_scores)):
            collected_recall_scores.append(final_scores[cur_id][which_num])
        # load the finegrained hypothesis checkpoint file to obtain cur_ttl_search_step
        if exp_type == "MC2":
            try:
                cur_finegrained_hyp_checkpoint_file_path = f"./Checkpoints/{job_name}/hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_{model_name}_{model_name}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_bkgid_{cur_bkg_id}_init_hyp_id_{init_hyp_id}_{job_name}.pkl"
                cur_bkg_hypothesis, cur_ttl_search_step = load_final_hypothesis_from_HGTree_with_reasoning_steps(cur_finegrained_hyp_checkpoint_file_path, hierarchy_id)
            except Exception as e:
                cur_finegrained_hyp_checkpoint_file_path = f"./Checkpoints/{job_name}/hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_{model_name}_{model_name}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_bkgid_{cur_bkg_id}_{job_name}.pkl"
                cur_bkg_hypothesis, cur_ttl_search_step = load_final_hypothesis_from_HGTree_with_reasoning_steps(cur_finegrained_hyp_checkpoint_file_path, hierarchy_id)
            collected_ttl_search_steps.append(cur_ttl_search_step)
    # calculate the mean and std of the collected recall scores
    print(f"Collected {len(collected_recall_scores)} recall scores.")
    mean_recall_score = np.mean(collected_recall_scores)
    std_recall_score = np.std(collected_recall_scores)
    if exp_type == "MC2":
        # calculate the mean and std of the collected ttl_search_steps
        print(f"Collected {len(collected_ttl_search_steps)} ttl_search_steps.")
        mean_ttl_search_step = np.mean(collected_ttl_search_steps)
        std_ttl_search_step = np.std(collected_ttl_search_steps)
    else:
        mean_ttl_search_step = 0
        std_ttl_search_step = 0
    return mean_recall_score, std_recall_score, mean_ttl_search_step, std_ttl_search_step






if __name__ == "__main__":
    # baseline_MC, MC_with_hint, MC_with_feedback_with_hint, MC_with_feedback_stronger_with_hint, MC2_with_MC_input_self_rank, MC2_with_MC_input_oracle_rank, \
    # MC2_with_feedback_oracle_rank, MC2_with_feedback_x2_oracle_rank, MC2_with_feedback_x3_oracle_rank, MC2_with_feedback_x4_oracle_rank \
    # MC2_with_feedback_x2_oracle_rank_only_1_feedback
    # MC2_with_feedback_v2_x2_oracle_rank
    # baseline_MC_baseline_1, baseline_MC_baseline_2
    # MC_with_hint_vague_cg_hyp, MC_with_hint_vague_cg_hyp_MOOSE
    job_name = "baseline_MC_baseline_1"
    model_name = "gpt-4o-mini"
    model_name_eval = None
    start_id = 0
    end_id = 10
    exp_type = "MC"
    # which_num: 0: precision, 1: recall, 2: f1, 3: weighted_precision, 4: weighted_recall, 5: weighted_f1
    which_num = 4
    mean_recall_score, std_recall_score, mean_ttl_search_step, std_ttl_search_step = summarize_result_with_reasoning_steps(job_name, model_name, model_name_eval, start_id, end_id, exp_type, which_num)
    print(f"The mean recall score of {job_name} is {mean_recall_score} with std {std_recall_score}")
    print(f"The mean ttl_search_step of {job_name} is {mean_ttl_search_step} with std {std_ttl_search_step}")