import os, sys, shutil, argparse, json
import demo_utils as utils
from external.MC2.Method.utils import load_chem_annotation


class MooseDemo:
    # job_name: name of the job, used in the names of the output files to be saved
    # bkg_id: background ID in TOMATO-Chem benchmark; if use custom research background, set it to 0
    def __init__(self, api_type, api_key, base_url, model_name, job_name, bkg_id=0, api_type_eval=None, api_key_eval=None, base_url_eval=None, model_name_eval=None):
        # api basic info
        assert api_type in [0, 1, 2], "api_type must be 0 (openai) or 1 (azure) or 2 (google)"
        # inference api basic info
        self.api_type = api_type
        self.api_key = api_key
        self.base_url = base_url
        self.model_name = model_name
        # evaluation api basic info
        self.api_type_eval = api_type if api_type_eval is None else api_type_eval
        self.api_key_eval = api_key if api_key_eval is None else api_key_eval
        self.base_url_eval = base_url if base_url_eval is None else base_url_eval
        self.model_name_eval = model_name if model_name_eval is None else model_name_eval
        # job identifier
        self.job_name = job_name
        self.bkg_id = bkg_id
        # create directories if not exist
        if not os.path.exists("Checkpoints"):
            os.makedirs("Checkpoints")
        if not os.path.exists("StartFiles"):
            os.makedirs("StartFiles")
        # mkdir folder for each job in both checkpoints and start files
        os.makedirs(f"./StartFiles/{job_name}", exist_ok=True)
        os.makedirs(f"./Checkpoints/{job_name}", exist_ok=True)
        # every job, specified by [job_name, bkg_id, init_id/init_hyp_id], is assigned with fixed and unique paths to its custom start files, and MC/MC2 checkpoint files
        self.list_custom_MC_research_background_path = []
        self.list_custom_MC_inspiration_corpus_path = []
        self.list_custom_MC2_research_background_and_coarse_hyp_path = []


    # ==================== Write Start File from Scratch (Start File used to Run MC/MC2) ==================== #

    def write_MC_start_file_research_background(self, research_question, background_survey, init_id):
        custom_MC_research_background_path = utils.full_custom_MC_start_file_research_background_path(self.job_name, self.bkg_id, init_id)
        if custom_MC_research_background_path not in self.list_custom_MC_research_background_path:
            self.list_custom_MC_research_background_path.append(custom_MC_research_background_path)
        # assert not os.path.exists(self.custom_MC_research_background_path), "Custom research background file already exists."
        utils.write_MC_start_file_research_background(research_question, background_survey, custom_MC_research_background_path)

    
    def write_MC_start_file_inspiration_corpus(self, raw_insp_xlsx_dir, init_id):
        custom_MC_inspiration_corpus_path = utils.full_custom_MC_start_file_inspiration_corpus_path(self.job_name, self.bkg_id, init_id)
        if custom_MC_inspiration_corpus_path not in self.list_custom_MC_inspiration_corpus_path:
            self.list_custom_MC_inspiration_corpus_path.append(custom_MC_inspiration_corpus_path)
        # assert not os.path.exists(self.custom_MC_inspiration_corpus_path), "Custom inspiration corpus file already exists."
        utils.write_MC_start_file_inspiration_corpus(raw_insp_xlsx_dir, custom_MC_inspiration_corpus_path)


    # will write a start file no matter whether it already exists
    def write_MC2_start_file(self, research_question, background_survey, coarse_grained_hypothesis, init_hyp_id):
        cur_custom_MC2_start_file_path = utils.full_custom_MC2_start_file_path(self.job_name, self.bkg_id, init_hyp_id)
        print("cur_custom_MC2_start_file_path", cur_custom_MC2_start_file_path)
        if cur_custom_MC2_start_file_path not in self.list_custom_MC2_research_background_and_coarse_hyp_path:
            self.list_custom_MC2_research_background_and_coarse_hyp_path.append(cur_custom_MC2_start_file_path)
        # assert not os.path.exists(cur_custom_MC2_start_file_path), "Custom MC2 research background and coarse hypothesis file already exists."
        utils.write_MC2_start_file(research_question, background_survey, coarse_grained_hypothesis, cur_custom_MC2_start_file_path)


    # ==================== Initialize Start File with Existing Ones (Start File used to Run MC/MC2) (might not be needed for the website demo) ==================== #

    def initialize_custom_MC_research_background_with_an_existing_file(self, another_MC_research_background_path, init_id):
        # this file does not exist, and another file exists
        assert os.path.exists(another_MC_research_background_path), "Another research background file (to initialize this custom background file) does not exist."
        # Copy and rename
        custom_MC_research_background_path = utils.full_custom_MC_start_file_research_background_path(self.job_name, self.bkg_id, init_id)
        if custom_MC_research_background_path not in self.list_custom_MC_research_background_path:
            self.list_custom_MC_research_background_path.append(custom_MC_research_background_path)
        # assert not os.path.exists(custom_MC_research_background_path), "Custom research background file already exists."
        shutil.copy(another_MC_research_background_path, custom_MC_research_background_path)


    def initialize_custom_MC_inspiration_corpus_with_an_existing_file(self, another_MC_inspiration_corpus_path, init_id):
        # this file does not exist, and another file exists
        assert os.path.exists(another_MC_inspiration_corpus_path), "Another inspiration corpus file (to initialize this custom corpus file) does not exist."
        # Copy and rename
        custom_MC_inspiration_corpus_path = utils.full_custom_MC_start_file_inspiration_corpus_path(self.job_name, self.bkg_id, init_id)
        if custom_MC_inspiration_corpus_path not in self.list_custom_MC_inspiration_corpus_path:
            self.list_custom_MC_inspiration_corpus_path.append(custom_MC_inspiration_corpus_path)
        # assert not os.path.exists(custom_MC_inspiration_corpus_path), "Custom inspiration corpus file already exists."
        shutil.copy(another_MC_inspiration_corpus_path, custom_MC_inspiration_corpus_path)


    def initialize_custom_MC2_research_background_and_coarse_hyp_with_an_existing_file(self, another_MC2_research_background_and_coarse_hyp_path, init_hyp_id):
        # this file does not exist, and another file exists
        assert os.path.exists(another_MC2_research_background_and_coarse_hyp_path), "Another MC2 research background and coarse hypothesis file (to initialize this custom file) does not exist."
        # Copy and rename
        cur_custom_MC2_start_file_path = utils.full_custom_MC2_start_file_path(self.job_name, self.bkg_id, init_hyp_id)
        if cur_custom_MC2_start_file_path not in self.list_custom_MC2_research_background_and_coarse_hyp_path:
            self.list_custom_MC2_research_background_and_coarse_hyp_path.append(cur_custom_MC2_start_file_path)
        # assert not os.path.exists(cur_custom_MC2_start_file_path), "Custom MC2 research background and coarse hypothesis file already exists."
        shutil.copy(another_MC2_research_background_and_coarse_hyp_path, cur_custom_MC2_start_file_path)    


    # ==================== Run MC/MC2 ==================== #

    # INPUT:
    #   (deprecated) bkg_id: background ID in TOMATO-Chem benchmark; if use custom background, set it to 0
    #   which_stage: [0/1, 0/1, 0/1] representing whether perform [inspiration retrieval, hypothesis composition, hypothesis ranking] respectively
    #   if_eval_with_gdth_hyp: 0/1, whether to evaluate the hypotheses with groundtruth hypothesis annotation (by default, only the research question in the TOMATO-Chem benchmark has the groundtruth hypothesis annotation); only used when which_stage[2] is 1
    def run_MC(self, init_id, which_stage=None, if_eval_with_gdth_hyp=0):
        if which_stage is None:
            which_stage = [1, 1, 1]
        custom_MC_research_background_path = utils.full_custom_MC_start_file_research_background_path(self.job_name, self.bkg_id, init_id)
        custom_MC_inspiration_corpus_path = utils.full_custom_MC_start_file_inspiration_corpus_path(self.job_name, self.bkg_id, init_id)
        assert os.path.exists(custom_MC_research_background_path), "Custom research background file does not exist."
        assert os.path.exists(custom_MC_inspiration_corpus_path), "Custom inspiration corpus file does not exist."
        utils.run_MC_py(self.api_type, self.api_key, self.base_url, self.model_name, self.model_name, self.model_name, custom_MC_research_background_path, custom_MC_inspiration_corpus_path, which_stage, bkg_id=self.bkg_id,init_id=init_id, output_dir_postfix=self.job_name, if_eval_with_gdth_hyp=if_eval_with_gdth_hyp)
        # utils.run_MC(self.api_type, self.api_key, self.base_url, self.model_name, self.model_name, self.model_name, custom_MC_research_background_path, custom_MC_inspiration_corpus_path, which_stage, bkg_id=self.bkg_id, output_dir_postfix=self.job_name, if_eval_with_gdth_hyp=if_eval_with_gdth_hyp, init_id=init_id)


    # INPUT:
    #   (deprecated) bkg_id: background ID in TOMATO-Chem benchmark; if use custom background, set it to 0
    def run_MC2(self, init_hyp_id):
        # obtain start file path
        cur_custom_MC2_start_file_path = utils.full_custom_MC2_start_file_path(self.job_name, self.bkg_id, init_hyp_id)
        assert os.path.exists(cur_custom_MC2_start_file_path), "Custom MC2 research background and coarse hypothesis file does not exist."
        utils.run_MC2_py(self.api_type, self.api_key, self.base_url, self.model_name, self.model_name,
                         cur_custom_MC2_start_file_path, bkg_id=self.bkg_id, output_dir_postfix=self.job_name,
                         init_hyp_id=init_hyp_id)
        # utils.run_MC2(self.api_type, self.api_key, self.base_url, self.model_name, self.model_name, cur_custom_MC2_start_file_path, bkg_id=self.bkg_id, output_dir_postfix=self.job_name, init_hyp_id=init_hyp_id)


    # ==================== Simulated Human Feedback (for HAII) ==================== #

    # INPUT:
    #   selected_gene_hyp: the selected gene hypothesis to provide feedback
    # Output:
    #   feedback: text
    def obtain_feedback_simulated(self, selected_gene_hyp):
        # load research question and groundtruth hypothesis from TOMATO-Chem benchmark data
        bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")
        research_question = bkg_q[self.bkg_id]
        background_survey = dict_bkg2survey[research_question]
        gdth_hyp = dict_bkg2fg_hyp[research_question]

        # simulated feedback
        feedback = utils.provide_feedback(research_question, gdth_hyp, selected_gene_hyp, self.api_type, self.api_key, self.base_url, self.model_name)
        return feedback

    
    # FUNCTION:
    #   Obtain inspiration hints (in concise keywords) to simulate scientist's (rough and accurate) judgement on research direction before running MC/MC2
    def obtain_hint_simulated(self):
        # load TOMATO-Chem benchmark data
        bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")
        research_question = bkg_q[self.bkg_id]
        hint_keywords = dict_bkg2note[research_question]

        hint_text = utils.gdth_insp_keyword_to_text(hint_keywords)
        return hint_text
    

    # ==================== Use Human Feedback to Update Start Files (for HAII) ==================== #

    # new_content: text as the new content to append to the survey in the start file of MC
    # clean_up_survey_from_first_selected_hyp_and_feedback: 0/1, whether to clean up the first selected hyp and feedback from the survey
    def append_new_content_to_background_survey_in_start_file_MC(self, new_content, init_id, clean_up_survey_from_first_selected_hyp_and_feedback=0):
        custom_MC_research_background_path = utils.full_custom_MC_start_file_research_background_path(self.job_name, self.bkg_id, init_id)
        assert os.path.exists(custom_MC_research_background_path), "Custom research background file does not exist."
        # load existing content
        with open(custom_MC_research_background_path, 'r') as f:
            cur_research_question, cur_background_survey = json.load(f)
        if clean_up_survey_from_first_selected_hyp_and_feedback:
            prompts = utils.demo_instruction_prompts("obtain_selected_hyp_and_feedback_text")
            assert len(prompts) == 2, "prompts should have 2 elements."
            cur_background_survey_split = cur_background_survey.split(prompts[0].strip().split("\n")[0])
            num_existing_selected_hyp_and_feedback = len(cur_background_survey_split) - 1
            if num_existing_selected_hyp_and_feedback > 0:
                cur_background_survey = cur_background_survey_split[0].strip()
                print(f"{num_existing_selected_hyp_and_feedback} existing selected hyp and feedback is cleaned up from the survey.")
            else:
                print("No existing selected hyp and feedback to be cleaned up from the survey.")
        # update content
        cur_background_survey += "\n" + new_content
        # write back to file
        with open(custom_MC_research_background_path, 'w') as f:
            json.dump([cur_research_question, cur_background_survey], f)
        print("\nUpdated Background Survey: \n", cur_background_survey)


    # new_content: text as the new content to append to the survey in the start file of MC2
    # clean_up_survey_from_first_selected_hyp_and_feedback: 0/1, whether to clean up the first selected hyp and feedback from the survey
    def append_new_content_to_background_survey_in_start_file_MC2(self, new_content, init_hyp_id, clean_up_survey_from_first_selected_hyp_and_feedback=0):
        cur_custom_MC2_start_file_path = utils.full_custom_MC2_start_file_path(self.job_name, self.bkg_id, init_hyp_id)
        assert os.path.exists(cur_custom_MC2_start_file_path), "Custom MC2 research background and coarse hypothesis file does not exist."
        # load existing content
        with open(cur_custom_MC2_start_file_path, 'r') as f:
            start_data = json.load(f)
        # each custom start file only contains one research question
        cur_research_question, cur_background_survey, cur_coarse_grained_hypothesis = start_data[0]
        if clean_up_survey_from_first_selected_hyp_and_feedback:
            prompts = utils.demo_instruction_prompts("obtain_selected_hyp_and_feedback_text")
            assert len(prompts) == 2, "prompts should have 2 elements."
            cur_background_survey_split = cur_background_survey.split(prompts[0].strip().split("\n")[0])
            num_existing_selected_hyp_and_feedback = len(cur_background_survey_split) - 1
            if num_existing_selected_hyp_and_feedback > 0:
                cur_background_survey = cur_background_survey_split[0].strip()
                print(f"{num_existing_selected_hyp_and_feedback} existing selected hyp and feedback is cleaned up from the survey.")
            else:
                print("No existing selected hyp and feedback to be cleaned up from the survey.")
        # update content
        cur_background_survey += "\n\n" + new_content
        # write back to file
        with open(cur_custom_MC2_start_file_path, 'w') as f:
            json.dump([[cur_research_question, cur_background_survey, cur_coarse_grained_hypothesis]], f)
        print("\nUpdated Background Survey: \n", cur_background_survey)


    # ==================== Evaluate MC and MC2's hypothesis with groundtruth hypothesis annotation (TOMATO-Chem) ==================== #

    # INPUT:
    #   num_hyp_for_eval: number of hypotheses to evaluate (default: 10); it is set because many hypotheses are generated in the MC process, and we only want to evaluate the top-k hypotheses (MC2 won't generate many hypotheses)
    # Output:
    #   final_hypothesis_with_ancillary_info: [[hypothesis, score, scores_list, num_rounds], ...]
    #   final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]
    #       len(final_scores) == num_hyp_for_eval; len(final_hypothesis_with_ancillary_info) normally is larger than num_hyp_for_eval
    def evaluate_MC_hypothesis_with_groundtruth_hypothesis_annotation(self, init_id, num_hyp_for_eval=10, num_compare_times=3, chem_annotation_path="./external/MC2/Data/chem_research_2024_finegrained.xlsx", preprocess_groundtruth_components_dir="./Checkpoints/groundtruth_hyp_components_collection.json", hyp_type='hyp'):
        ## Using MC's evaluation
        # self.run_MC(which_stage=[0, 0, 1], if_eval_with_gdth_hyp=1)
        # # load matched scores file
        # final_hypothesis, final_scores = utils.load_MC_matched_scores(self.job_name, self.model_name, init_id, self.bkg_id)

        ## Using MC2's evaluation
        # final_hypothesis_with_ancillary_info: [[hypothesis, score, scores_list, num_rounds], ...]
        final_hypothesis_with_ancillary_info = utils.load_MC_gene_hypothesis(self.job_name, self.model_name, init_id, self.bkg_id)
        # assert final_hypothesis_with_ancillary_info is sorted based on the score
        final_hypothesis_with_ancillary_info.sort(key=lambda x: x[1], reverse=True)
        final_hypothesis = [hyp[0] for hyp in final_hypothesis_with_ancillary_info[:num_hyp_for_eval]]
        final_hypothesis_score_no_reference = [hyp[1] for hyp in final_hypothesis_with_ancillary_info[:num_hyp_for_eval]]
        # check whether the scores are sorted in descending order
        print("final_hypothesis_score_no_reference: ", final_hypothesis_score_no_reference)

        final_scores = utils.evaluate_MC2_hyp_with_gdth_reference(self.api_type_eval, self.api_key_eval, self.base_url_eval, self.model_name_eval, chem_annotation_path, preprocess_groundtruth_components_dir, hyp_type, num_compare_times, final_hypothesis, self.bkg_id)
        return final_hypothesis_with_ancillary_info, final_scores


    # Output:
    #   final_hypothesis: [hyp0, hyp1, ...]
    #   final_scores: [[precision, recall, f1, weighted_precision, weighted_recall, weighted_f1], ...]
    #       len(final_scores) == len(final_hypothesis)
    def evaluate_MC2_hypothesis_with_groundtruth_hypothesis_annotation(self, init_hyp_id, num_compare_times=3, chem_annotation_path="./external/MC2/Data/chem_research_2024_finegrained.xlsx", preprocess_groundtruth_components_dir="./Checkpoints/groundtruth_hyp_components_collection.json", hyp_type='hyp'):
        # final_hypothesis: [hyp]
        final_hypothesis = utils.load_MC2_gene_hypothesis(self.job_name, self.model_name, self.model_name, init_hyp_id, self.bkg_id)

        final_scores = utils.evaluate_MC2_hyp_with_gdth_reference(self.api_type_eval, self.api_key_eval, self.base_url_eval, self.model_name_eval, chem_annotation_path, preprocess_groundtruth_components_dir, hyp_type, num_compare_times, final_hypothesis, self.bkg_id)
        return final_hypothesis, final_scores
        





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='MOOSE Demo')
    # inference API
    parser.add_argument("--api_type", type=int, help="0: openai's API toolkit; 1: azure's API toolkit")
    parser.add_argument("--api_key", type=str, help="your API key for OpenAI or Azure")
    parser.add_argument("--base_url", type=str, help="base url for the API")
    parser.add_argument("--model_name", type=str, help="e.g., gpt-4o")
    # evaluation API
    parser.add_argument("--api_type_eval", type=int, help="0: openai's API toolkit; 1: azure's API toolkit; 2: google's API toolkit")
    parser.add_argument("--api_key_eval", type=str, help="your API key for OpenAI or Azure")
    parser.add_argument("--base_url_eval", type=str, help="base url for the API")
    parser.add_argument("--model_name_eval", type=str, help="used for evaluate the recall of the generated hypotheses with groundtruth hypothesis reference")
    # job parameters
    parser.add_argument("--bkg_id", type=int, help="background ID in TOMATO-Chem benchmark; else the id in the custom input file")
    parser.add_argument("--job_name", type=str, default="demo_job", help="name of the job, used in the names of the output files to be saved")
    args = parser.parse_args()

    assert args.api_type in [0, 1, 2], "api_type must be 0 (openai) or 1 (azure) or 2 (google)"
    assert args.api_key is not None, "API key must be provided"
    assert args.base_url is not None, "Base URL must be provided"

    moose_demo = MooseDemo(args.api_type, args.api_key, args.base_url, args.model_name, job_name=args.job_name, bkg_id=args.bkg_id, api_type_eval=args.api_type_eval, api_key_eval=args.api_key_eval, base_url_eval=args.base_url_eval, model_name_eval=args.model_name_eval)