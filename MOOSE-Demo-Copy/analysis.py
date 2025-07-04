import json
import glob
import numpy as np

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




if __name__ == "__main__":
    # baseline_MC, MC_with_hint, MC_with_feedback_with_hint, MC_with_feedback_stronger_with_hint, MC2_with_MC_input_self_rank, MC2_with_MC_input_oracle_rank, MC2_with_feedback_oracle_rank
    job_name = "MC2_with_MC_input_oracle_rank"
    model_name = "gpt-4o-mini"
    model_name_eval = None
    mean_recall_score, std_recall_score = summarize_result(job_name, model_name, model_name_eval)
    print(f"The mean recall score of {job_name} is {mean_recall_score} with std {std_recall_score}.")