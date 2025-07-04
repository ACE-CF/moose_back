import os
import subprocess
import argparse
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = sys.executable

def run(command_list):
    command_list = [str(x) for x in command_list]
    print("Running:", " ".join(command_list))
    subprocess.run(command_list, check=True)

def run_mc_pipeline(
    api_type, api_key, base_url,
    model_name_insp_retrieval, model_name_gene, model_name_eval,
    custom_research_background_path, custom_inspiration_corpus_path,
    if_retrieval, if_generation, if_evaluation,
    bkg_id, init_id,output_dir_postfix, if_with_gdth_hyp_annotation
):
    checkpoint_root_dir = "./Checkpoints"
    startfiles_root_dir = "./StartFiles"
    chem_annotation_path = "./external/MC/Data/chem_research_2024.xlsx"

    script_path = os.path.join(BASE_DIR, "external", "MC", "Method", "inspiration_screening.py")
    script_path2 = os.path.join(BASE_DIR, "external", "MC", "Method", "hypothesis_generation.py")
    script_path3 = os.path.join(BASE_DIR, "external", "MC", "Method", "evaluate.py")

    # Step 1: Inspiration Retrieval
    if if_retrieval == 1:
        # print(custom_research_background_path)
        # print(custom_inspiration_corpus_path)
        run([
            PYTHON_EXECUTABLE, "-u", script_path,
            "--model_name", model_name_insp_retrieval,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", chem_annotation_path,
            "--output_dir", f"{checkpoint_root_dir}/{output_dir_postfix}/coarse_inspiration_search_{model_name_insp_retrieval}_{bkg_id}_{init_id}_{output_dir_postfix}.json",
            "--corpus_size", "150",
            "--if_use_background_survey", "1",
            "--if_use_strict_survey_question", "1",
            "--num_screening_window_size", "15",
            "--num_screening_keep_size", "3",
            "--num_round_of_screening", "4",
            "--if_save", "1",
            "--background_question_id", "0",
            "--if_select_based_on_similarity", "0",
            "--custom_research_background_path", custom_research_background_path,
            "--custom_inspiration_corpus_path", custom_inspiration_corpus_path
        ])

    # Step 2: Hypothesis Generation
    if if_generation == 1:
        run([
            PYTHON_EXECUTABLE, "-u", script_path2,
            "--model_name", model_name_gene,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", chem_annotation_path,
            "--corpus_size", "150",
            "--if_use_strict_survey_question", "1",
            "--if_use_background_survey", "1",
            "--inspiration_dir", f"{checkpoint_root_dir}/{output_dir_postfix}/coarse_inspiration_search_{model_name_insp_retrieval}_{bkg_id}_{init_id}_{output_dir_postfix}.json",
            "--output_dir", f"{checkpoint_root_dir}/{output_dir_postfix}/hypothesis_generation_{model_name_gene}_{bkg_id}_{init_id}_{output_dir_postfix}.json",
            "--if_save", "1",
            "--if_load_from_saved", "0",
            "--if_use_gdth_insp", "0",
            "--idx_round_of_first_step_insp_screening", "1",
            "--num_mutations", "2",
            "--num_itr_self_refine", "2",
            "--num_self_explore_steps_each_line", "3",
            "--num_screening_window_size", "12",
            "--num_screening_keep_size", "2",
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
            "--custom_research_background_path", custom_research_background_path,
            "--custom_inspiration_corpus_path", custom_inspiration_corpus_path
        ])

    # Step 3: Evaluation
    if if_evaluation == 1:
        run([
            PYTHON_EXECUTABLE, "-u", script_path3,
            "--model_name", model_name_eval,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", chem_annotation_path,
            "--corpus_size", "150",
            "--hypothesis_dir", f"{checkpoint_root_dir}/{output_dir_postfix}/hypothesis_generation_{model_name_gene}_{bkg_id}_{init_id}_{output_dir_postfix}.json",
            "--output_dir", f"{checkpoint_root_dir}/{output_dir_postfix}/evaluation_{if_with_gdth_hyp_annotation}_{model_name_eval}_{bkg_id}_{init_id}_{output_dir_postfix}.json",
            "--if_save", "1",
            "--if_load_from_saved", "0",
            "--if_with_gdth_hyp_annotation", if_with_gdth_hyp_annotation,
            "--custom_inspiration_corpus_path", custom_inspiration_corpus_path
        ])

# 用于独立运行测试（可选）
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("api_type")
    parser.add_argument("api_key")
    parser.add_argument("base_url")
    parser.add_argument("model_name_insp_retrieval")
    parser.add_argument("model_name_gene")
    parser.add_argument("model_name_eval")
    parser.add_argument("custom_research_background_path")
    parser.add_argument("custom_inspiration_corpus_path")
    parser.add_argument("if_retrieval", type=int)
    parser.add_argument("if_generation", type=int)
    parser.add_argument("if_evaluation", type=int)
    parser.add_argument("bkg_id")
    parser.add_argument("init_id")
    parser.add_argument("output_dir_postfix")
    parser.add_argument("if_with_gdth_hyp_annotation")

    args = parser.parse_args()

    run_mc_pipeline(
        args.api_type,
        args.api_key,
        args.base_url,
        args.model_name_insp_retrieval,
        args.model_name_gene,
        args.model_name_eval,
        args.custom_research_background_path,
        args.custom_inspiration_corpus_path,
        args.if_retrieval,
        args.if_generation,
        args.if_evaluation,
        args.bkg_id,
        args.init_id,
        args.output_dir_postfix,
        args.if_with_gdth_hyp_annotation
    )
