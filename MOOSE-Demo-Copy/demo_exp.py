import os, sys, argparse, json
from MooseDemo import MooseDemo
import demo_utils as utils
from external.MC2.Method.utils import load_chem_annotation


bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")


def baseline_MC(args, job_name, if_eval_with_gdth_hyp, start_id, end_id, if_save):
    assert start_id >= 0 and end_id <= len(bkg_q), "start_id and end_id must be within the range of bkg_q."
    for cur_id in range(start_id, end_id+1):
        # check if result file already exists
        result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{args.model_name}_eval_model_name_{args.model_name_eval}.json"
        if os.path.exists(result_file_name_eval_with_gdth_hyp):
            print(f"Warning:The result file already exists, skipping background question {cur_id}.")
            continue
        # initialize MooseDemo with the task name and current background question ID
        moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, cur_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
        # load research question and background survey
        research_question = bkg_q[cur_id]
        background_survey = dict_bkg2survey[research_question]
        # prepare start files
        moose_demo.write_MC_start_file_research_background(research_question, background_survey)        
        moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file("./external/MC/Data/Inspiration_Corpus_150.json")
        # run MC
        which_stage = [1, 1, 1]
        moose_demo.run_MC(which_stage)
        # evaluate with ground truth hypothesis annotation
        if if_eval_with_gdth_hyp:
            if not os.path.exists(result_file_name_eval_with_gdth_hyp):
                final_hypothesis, final_scores = moose_demo.evaluate_MC_hypothesis_with_groundtruth_hypothesis_annotation()
                # save result
                if if_save:
                    with open(result_file_name_eval_with_gdth_hyp, "w") as f:
                        json.dump([final_hypothesis, final_scores], f)
            else:
                print("The result file already exists, skipping evaluation with ground truth hypothesis annotation.")




def MC_with_hint(args, job_name, if_eval_with_gdth_hyp, start_id, end_id, if_save):
    # This function is similar to baseline_MC, but it provides hints to the user based on the background question.
    assert start_id >= 0 and end_id <= len(bkg_q), "start_id and end_id must be within the range of bkg_q."
    for cur_id in range(start_id, end_id+1):
        # check if result file already exists
        result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{args.model_name}_eval_model_name_{args.model_name_eval}.json"
        if os.path.exists(result_file_name_eval_with_gdth_hyp):
            print(f"The result file already exists, skipping background question {cur_id}.")
            continue
        # initialize MooseDemo with the task name and current background question ID
        moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, cur_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
        # load research question and background survey
        research_question = bkg_q[cur_id]
        background_survey = dict_bkg2survey[research_question]
        # prepare start files
        moose_demo.write_MC_start_file_research_background(research_question, background_survey)
        moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file("./external/MC/Data/Inspiration_Corpus_150.json")
        # provide hint (update start files)
        hint_keywords = dict_bkg2note[research_question]
        hint_text_to_append = utils.gdth_insp_keyword_to_text(hint_keywords)
        moose_demo.append_new_content_to_background_survey_in_start_file_MC(hint_text_to_append, clean_up_survey_from_first_selected_hyp_and_feedback=0)
        # run MC
        which_stage = [1, 1, 1]
        moose_demo.run_MC(which_stage)
        # evaluate with ground truth hypothesis annotation
        if if_eval_with_gdth_hyp:
            if not os.path.exists(result_file_name_eval_with_gdth_hyp):
                final_hypothesis, final_scores = moose_demo.evaluate_MC_hypothesis_with_groundtruth_hypothesis_annotation()
                # save result
                if if_save:
                    with open(result_file_name_eval_with_gdth_hyp, "w") as f:
                        json.dump([final_hypothesis, final_scores], f)
            else:
                print("The result file already exists, skipping evaluation with ground truth hypothesis annotation.")


def MC_with_feedback(args, prev_MC_job_name, job_name, if_eval_with_gdth_hyp, start_id, end_id, if_save, select_hyp_from_ckpt_method):
    # This function is similar to MC_with_hint, but it also provides feedback on the user's hypothesis.
    assert start_id >= 0 and end_id <= len(bkg_q), "start_id and end_id must be within the range of bkg_q."
    for cur_id in range(start_id, end_id+1):
        # check if result file already exists
        result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{args.model_name}_eval_model_name_{args.model_name_eval}.json"
        if os.path.exists(result_file_name_eval_with_gdth_hyp):
            print(f"Warning: The result file already exists, skipping background question {cur_id}.")
            continue
        # initialize MooseDemo with the task name and current background question ID
        moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, cur_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
        # prepare start files
        moose_demo.initialize_custom_MC_research_background_with_an_existing_file(f"./StartFiles/{prev_MC_job_name}/{prev_MC_job_name}_bkg_id_{cur_id}_custom_MC_research_background.json")
        moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file("./external/MC/Data/Inspiration_Corpus_150.json")
        # select a hypothesis and provide feedback
        if select_hyp_from_ckpt_method == "best_recall":
            selected_coarse_grained_hyp, best_recall_score = utils.load_best_recall_hypothesis_from_ckpt(prev_MC_job_name, cur_id, args.model_name, args.model_name_eval, which_experiment='MC')
        elif select_hyp_from_ckpt_method == "best_self_eval":
            selected_coarse_grained_hyp = utils.load_MC_gene_hypothesis(prev_MC_job_name, args.model_name, cur_id)[0][0]
        else:
            raise NotImplementedError(select_hyp_from_ckpt_method)
        feedback = moose_demo.obtain_feedback_simulated(selected_coarse_grained_hyp)
        # update feedback in start file
        feedback_text_to_append = utils.obtain_selected_hyp_and_feedback_text(selected_coarse_grained_hyp, feedback)
        moose_demo.append_new_content_to_background_survey_in_start_file_MC(feedback_text_to_append, clean_up_survey_from_first_selected_hyp_and_feedback=1)
        # run MC
        which_stage = [1, 1, 1]
        moose_demo.run_MC(which_stage)  
        # evaluate with ground truth hypothesis annotation
        if if_eval_with_gdth_hyp:
            if not os.path.exists(result_file_name_eval_with_gdth_hyp):
                final_hypothesis, final_scores = moose_demo.evaluate_MC_hypothesis_with_groundtruth_hypothesis_annotation()
                # save result
                if if_save:
                    with open(result_file_name_eval_with_gdth_hyp, "w") as f:
                        json.dump([final_hypothesis, final_scores], f)
            else:
                print("The result file already exists, skipping evaluation with ground truth hypothesis annotation.")



def MC2_with_MC_input(args, prev_MC_job_name, job_name, if_eval_with_gdth_hyp, start_id, end_id, if_save, select_hyp_from_ckpt_method):
    assert start_id >= 0 and end_id <= len(bkg_q), "start_id and end_id must be within the range of bkg_q."
    for cur_id in range(start_id, end_id+1):
        # check if result file already exists
        result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{args.model_name}_eval_model_name_{args.model_name_eval}.json"
        if os.path.exists(result_file_name_eval_with_gdth_hyp):
            print(f"Warning: The result file already exists, skipping background question {cur_id}.")
            continue
        # initialize MooseDemo with the task name and current background question ID
        moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, cur_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
        # load research question and background survey (original)
        ori_research_question = bkg_q[cur_id]
        ori_background_survey = dict_bkg2survey[ori_research_question]
        # load research question and background survey (from the start file of a previous MC job, which might add some additional information in the background survey)
        research_question, background_survey = utils.load_MC_start_file_research_background(prev_MC_job_name, cur_id)
        # check the consistency of the research question and background survey
        assert ori_research_question == research_question, "The research question in the start file of the previous MC job is not the same as the original research question."
        assert ori_background_survey in background_survey, "background_survey might append additional information to original background survey."
        # select a hypothesis from MC's output
        if select_hyp_from_ckpt_method == "best_self_eval":
            ## load coarse-grained hypothesis from MC's best self-evaluated hypothesis (without reference)
            # gene_hyp_list_raw: [[hypothesis, score, scores_list, num_rounds], ...]
            gene_hyp_list_raw = utils.load_MC_gene_hypothesis(prev_MC_job_name, args.model_name, cur_id)
            selected_coarse_grained_hyp = gene_hyp_list_raw[0][0]
        elif select_hyp_from_ckpt_method == "best_recall":
            ## load coarse-grained hypothesis from MC's best recall hypothesis (with reference)
            selected_coarse_grained_hyp, best_recall_score = utils.load_best_recall_hypothesis_from_ckpt(prev_MC_job_name, cur_id, args.model_name, args.model_name_eval, which_experiment='MC')
        else:
            raise NotImplementedError(select_hyp_from_ckpt_method)
        # prepare start files
        moose_demo.write_MC2_start_file(research_question, background_survey, selected_coarse_grained_hyp)
        # run MC2
        moose_demo.run_MC2()
        # evaluate with ground truth hypothesis annotation
        if if_eval_with_gdth_hyp:
            if not os.path.exists(result_file_name_eval_with_gdth_hyp):
                final_hypothesis, final_scores = moose_demo.evaluate_MC2_hypothesis_with_groundtruth_hypothesis_annotation(init_hyp_id=0)    
                # save result
                if if_save:
                    with open(result_file_name_eval_with_gdth_hyp, "w") as f:
                        json.dump([final_hypothesis, final_scores], f)
            else:
                print("The result file already exists, skipping evaluation with ground truth hypothesis annotation.")




def MC2_with_feedback(args, prev_MC2_job_name, job_name, if_eval_with_gdth_hyp, start_id, end_id, if_save, select_hyp_from_ckpt_method):
    assert start_id >= 0 and end_id <= len(bkg_q), "start_id and end_id must be within the range of bkg_q."
    assert select_hyp_from_ckpt_method in ['best_recall'], f"currently do not support best_self_eval: {select_hyp_from_ckpt_method}"
    for cur_id in range(start_id, end_id+1):
        # check if result file already exists
        result_file_name_eval_with_gdth_hyp = f"./Checkpoints/{job_name}/Result_{job_name}_bkg_id_{cur_id}_model_name_{args.model_name}_eval_model_name_{args.model_name_eval}.json"
        if os.path.exists(result_file_name_eval_with_gdth_hyp):
            print(f"Warning: The result file already exists, skipping background question {cur_id}.")
            continue
        # initialize MooseDemo with the task name and current background question ID
        moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, cur_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
        # load the research question, background survey, and coarse-grained hypothesis from the start file of the previous MC2 job
        research_question, background_survey, start_hypothesis = utils.load_MC2_start_file_research_background_and_coarse_hyp(prev_MC2_job_name, cur_id)
        # select a hypothesis from previous MC2's output
        if select_hyp_from_ckpt_method == "best_recall":
            selected_fine_grained_hyp, best_recall_score = utils.load_best_recall_hypothesis_from_ckpt(prev_MC2_job_name, cur_id, args.model_name, args.model_name_eval, which_experiment='MC2')
        else:
            raise NotImplementedError(select_hyp_from_ckpt_method)
        # prepare start file
        moose_demo.write_MC2_start_file(research_question, background_survey, selected_fine_grained_hyp)
        # provide feedback to the selected hypothesis
        feedback = moose_demo.obtain_feedback_simulated(selected_fine_grained_hyp)
        # update the start file with the feedback
        feedback_text_to_append = utils.obtain_selected_hyp_and_feedback_text(selected_fine_grained_hyp, feedback)
        moose_demo.append_new_content_to_background_survey_in_start_file_MC2(feedback_text_to_append, init_hyp_id=0, clean_up_survey_from_first_selected_hyp_and_feedback=1)
        # run MC2
        moose_demo.run_MC2()
        # evaluate with ground truth hypothesis annotation
        if if_eval_with_gdth_hyp:
            if not os.path.exists(result_file_name_eval_with_gdth_hyp):
                final_hypothesis, final_scores = moose_demo.evaluate_MC2_hypothesis_with_groundtruth_hypothesis_annotation(init_hyp_id=0)
                # save result
                if if_save:
                    with open(result_file_name_eval_with_gdth_hyp, "w") as f:
                        json.dump([final_hypothesis, final_scores], f)
            else:
                print("The result file already exists, skipping evaluation with ground truth hypothesis annotation.")



def Thermocell(args, job_name, num_init_hyp_from_MC_to_MC2):
    assert "simple" in job_name or "extensive" in job_name
    # check if result file already exists
    bkg_id = 0
    moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name, bkg_id, args.api_type_eval, args.api_key_eval, args.base_url_eval, args.model_name_eval)
    # prepare start files for MC
    if "simple" in job_name:
        moose_demo.initialize_custom_MC_research_background_with_an_existing_file("./StartFiles/wanhao_background_simple.json")
    elif "extensive" in job_name:
        moose_demo.initialize_custom_MC_research_background_with_an_existing_file("./StartFiles/wanhao_background_extensive.json")
    else:
        raise NotImplementedError(job_name)
    moose_demo.initialize_custom_MC_inspiration_corpus_with_an_existing_file("./StartFiles/wanhao_inspiration_paper.json")
    # run MC
    which_stage = [1, 1, 1]
    moose_demo.run_MC(which_stage)
    # select the best hypothesis from MC's output using self_eval
    MC_result = utils.load_MC_gene_hypothesis(job_name, args.model_name)
    # save the MC_result to a file
    with open(f"./Checkpoints/{job_name}/MC_result_{job_name}_{args.model_name}.json", "w") as f:
        json.dump(MC_result, f)
    # run MC2
    num_init_hyp_from_MC_to_MC2 = min(num_init_hyp_from_MC_to_MC2, len(MC_result))
    print(f"num_init_hyp_from_MC_to_MC2: {num_init_hyp_from_MC_to_MC2}")
    research_question, background_survey = utils.load_MC_start_file_research_background(job_name)
    # full_MC2_result: [[hyp1, hyp2], ...]
    full_MC2_result = []
    for init_hyp_id in range(num_init_hyp_from_MC_to_MC2):
        print(f"Running MC2 with init_hyp_id: {init_hyp_id}")
        selected_coarse_grained_hyp = MC_result[init_hyp_id][0]
        # prepare start files for MC2
        moose_demo.write_MC2_start_file(research_question, background_survey, selected_coarse_grained_hyp, init_hyp_id=init_hyp_id)
        # run MC2
        moose_demo.run_MC2(init_hyp_id=init_hyp_id)
        # load & save MC2's output
        cur_MC2_result = utils.load_MC2_gene_hypothesis(job_name, args.model_name, args.model_name_eval, init_hyp_id=init_hyp_id)
        full_MC2_result.append(cur_MC2_result)
        # save the full_MC2_result to a file
        with open(f"./Checkpoints/{job_name}/MC2_result_{job_name}_{args.model_name}.json", "w") as f:
            json.dump(full_MC2_result, f)




if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MOOSE Demo')
    # inference API
    parser.add_argument("--api_type", type=int, help="0: openai's API toolkit; 1: azure's API toolkit; 2: google's API toolkit")
    parser.add_argument("--api_key", type=str)
    parser.add_argument("--base_url", type=str, help="base url for the API")
    parser.add_argument("--model_name", type=str)
    # evaluation API
    parser.add_argument("--api_type_eval", type=int)
    parser.add_argument("--api_key_eval", type=str)
    parser.add_argument("--base_url_eval", type=str)
    parser.add_argument("--model_name_eval", type=str)
    # job parameters
    parser.add_argument("--job_name", type=str, default="test")
    parser.add_argument("--prev_job_name", type=str, nargs='?', const=None, help="the previous job name to load the checkpoint file for the current job; can be for both MC and MC2")
    parser.add_argument("--if_eval_with_gdth_hyp", type=int, default=0)
    parser.add_argument("--start_id", type=int)
    parser.add_argument("--end_id", type=int)
    parser.add_argument("--if_save", type=int, default=1)
    parser.add_argument("--select_hyp_from_ckpt_method", type=str, default="best_self_eval")
    parser.add_argument("--num_init_hyp_from_MC_to_MC2", type=int, default=5)
    args = parser.parse_args()

    assert args.api_type in [0, 1, 2], "api_type must be 0 (openai) or 1 (azure) or 2 (google)"
    assert args.api_key is not None, "API key must be provided"
    assert args.base_url is not None, "Base URL must be provided"
    assert args.model_name is not None, "Model name must be provided"
    assert args.if_save in [0, 1], "if_save must be 0 or 1"
    assert args.select_hyp_from_ckpt_method in ["best_self_eval", "best_recall"], "select_hyp_from_ckpt_method must be best_self_eval or best_recall"

    if not os.path.exists("Checkpoints"):
        os.makedirs("Checkpoints")
    if not os.path.exists("StartFiles"):
        os.makedirs("StartFiles")

    if "baseline_MC" in args.job_name:
        baseline_MC(args, job_name=args.job_name, if_eval_with_gdth_hyp=args.if_eval_with_gdth_hyp, start_id=args.start_id, end_id=args.end_id, if_save=args.if_save)
    elif "MC_with_hint" in args.job_name:
        MC_with_hint(args, job_name=args.job_name, if_eval_with_gdth_hyp=args.if_eval_with_gdth_hyp, start_id=args.start_id, end_id=args.end_id, if_save=args.if_save)
    elif "MC_with_feedback" in args.job_name:
        MC_with_feedback(args, prev_MC_job_name=args.prev_job_name, job_name=args.job_name, if_eval_with_gdth_hyp=args.if_eval_with_gdth_hyp, start_id=args.start_id, end_id=args.end_id, if_save=args.if_save, select_hyp_from_ckpt_method=args.select_hyp_from_ckpt_method)
    elif "MC2_with_MC_input" in args.job_name:
        MC2_with_MC_input(args, prev_MC_job_name=args.prev_job_name, job_name=args.job_name, if_eval_with_gdth_hyp=args.if_eval_with_gdth_hyp, start_id=args.start_id, end_id=args.end_id, if_save=args.if_save, select_hyp_from_ckpt_method=args.select_hyp_from_ckpt_method)
    elif "MC2_with_feedback" in args.job_name:
        MC2_with_feedback(args, prev_MC2_job_name=args.prev_job_name, job_name=args.job_name, if_eval_with_gdth_hyp=args.if_eval_with_gdth_hyp, start_id=args.start_id, end_id=args.end_id, if_save=args.if_save, select_hyp_from_ckpt_method=args.select_hyp_from_ckpt_method)
    elif "Thermocell" in args.job_name:
        Thermocell(args, job_name=args.job_name, num_init_hyp_from_MC_to_MC2=args.num_init_hyp_from_MC_to_MC2)
    else:
        raise NotImplementedError(args.job_name)