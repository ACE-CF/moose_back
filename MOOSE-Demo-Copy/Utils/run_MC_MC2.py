"""
Module for running MC and MC2 pipelines.
This module provides functions to run hypothesis generation pipelines.
"""

import os
import subprocess
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PYTHON_EXECUTABLE = sys.executable


def run(command_list):
    """Execute a command with real-time output streaming."""
    command_list = [str(x) for x in command_list]
    print("Running:", " ".join(command_list))

    process = subprocess.Popen(
        command_list,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    try:
        # Real-time line-by-line output reading
        for line in process.stdout:
            print(line, end='')
    except KeyboardInterrupt:
        print("\n" + "-"*27 + "C"*50 + "-"*27)
        print("\nKeyboardInterrupt received, terminating process...")
        process.terminate()
        process.wait()
        raise
    finally:
        if process.stdout:
            process.stdout.close()

    return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command_list)


def run_MC(api_type, api_key, base_url, model_name_insp_retrieval, model_name_gene, model_name_eval,
           custom_research_background_path, custom_inspiration_corpus_path, which_stage,
           bkg_id, output_dir_postfix, if_eval_with_gdth_hyp, init_id,
           if_mutate_inside_same_bkg_insp, if_mutate_between_diff_insp, baseline_type):
    """
    Run MC pipeline with three stages: inspiration retrieval, hypothesis composition, and hypothesis ranking.
    
    Args:
        api_type: API type (e.g., "openai")
        api_key: API key for the service
        base_url: Base URL for the API
        model_name_insp_retrieval: Model name for inspiration retrieval
        model_name_gene: Model name for hypothesis generation
        model_name_eval: Model name for hypothesis evaluation
        custom_research_background_path: Path to custom research background (empty string to use default)
        custom_inspiration_corpus_path: Path to custom inspiration corpus (empty string to use default)
        which_stage: List of 3 elements [0/1, 0/1, 0/1] for [retrieval, generation, evaluation]
        bkg_id: Background ID
        output_dir_postfix: Postfix for output directory
        if_eval_with_gdth_hyp: Whether to evaluate with ground truth hypothesis annotation
        init_id: Initial ID
        if_mutate_inside_same_bkg_insp: Whether to mutate inside same background inspiration
        if_mutate_between_diff_insp: Whether to mutate between different inspirations
        baseline_type: Type of baseline
    
    Returns:
        dict: Dictionary containing output file paths for each completed stage
    """
    
    # Validate inputs
    assert len(which_stage) == 3, "which_stage must be a list of 3 elements."
    assert all(x in [0, 1] for x in which_stage), "which_stage must contain only 0 or 1."
    
    # Set up paths
    checkpoint_root_dir = "./Checkpoints"
    output_dir = os.path.join(checkpoint_root_dir, output_dir_postfix) if output_dir_postfix else checkpoint_root_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert parameters to strings
    bkg_id_str = str(bkg_id)
    init_id_str = str(init_id)
    
    output_files = {}
    
    # Stage 1: Inspiration Retrieval
    if which_stage[0] == 1:
        print("\n" + "="*50)
        print("Stage 1: Inspiration Retrieval")
        print("="*50 + "\n")
        
        script = os.path.join(BASE_DIR, "external", "MC", "Method", "inspiration_screening.py")
        output_file = os.path.join(output_dir, 
            f"coarse_inspiration_search_{model_name_insp_retrieval}_{bkg_id_str}_{init_id_str}_{output_dir_postfix}.json")
        
        command = [
            PYTHON_EXECUTABLE, "-u", script,
            "--model_name", model_name_insp_retrieval,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", "./external/MC/Data/chem_research_2024.xlsx",
            "--output_dir", output_file,
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
        ]
        
        run(command)
        output_files['inspiration'] = output_file
    
    # Stage 2: Hypothesis Composition
    if which_stage[1] == 1:
        print("\n" + "="*50)
        print("Stage 2: Hypothesis Composition")
        print("="*50 + "\n")
        
        script = os.path.join(BASE_DIR, "external", "MC", "Method", "hypothesis_generation.py")
        inspiration_file = os.path.join(output_dir,
            f"coarse_inspiration_search_{model_name_insp_retrieval}_{bkg_id_str}_{init_id_str}_{output_dir_postfix}.json")
        output_file = os.path.join(output_dir,
            f"hypothesis_generation_{model_name_gene}_{bkg_id_str}_{init_id_str}_{output_dir_postfix}.json")
        
        command = [
            PYTHON_EXECUTABLE, "-u", script,
            "--model_name", model_name_gene,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", "./external/MC/Data/chem_research_2024.xlsx",
            "--corpus_size", "150",
            "--if_use_strict_survey_question", "1",
            "--if_use_background_survey", "1",
            "--inspiration_dir", inspiration_file,
            "--output_dir", output_file,
            "--if_save", "1",
            "--if_load_from_saved", "0",
            "--if_use_gdth_insp", "0",
            "--idx_round_of_first_step_insp_screening", "1",
            "--num_mutations", "2",
            "--num_itr_self_refine", "2",
            "--num_self_explore_steps_each_line", "3",
            "--num_screening_window_size", "12",
            "--num_screening_keep_size", "2",
            "--if_mutate_inside_same_bkg_insp", str(if_mutate_inside_same_bkg_insp),
            "--if_mutate_between_diff_insp", str(if_mutate_between_diff_insp),
            "--if_self_explore", "0",
            "--if_consider_external_knowledge_feedback_during_second_refinement", "0",
            "--inspiration_ids", "-1",
            # "--recom_inspiration_ids", "",
            "--recom_num_beam_size", "5",
            # "--self_explore_inspiration_ids", "",
            "--self_explore_num_beam_size", "5",
            "--max_inspiration_search_steps", "3",
            "--background_question_id", "0",
            "--custom_research_background_path", custom_research_background_path,
            "--custom_inspiration_corpus_path", custom_inspiration_corpus_path,
            "--baseline_type", str(baseline_type)
        ]
        
        run(command)
        output_files['hypothesis'] = output_file
    
    # Stage 3: Hypothesis Ranking
    if which_stage[2] == 1:
        print("\n" + "="*50)
        print("Stage 3: Hypothesis Ranking")
        print("="*50 + "\n")
        
        script = os.path.join(BASE_DIR, "external", "MC", "Method", "evaluate.py")
        hypothesis_file = os.path.join(output_dir,
            f"hypothesis_generation_{model_name_gene}_{bkg_id_str}_{init_id_str}_{output_dir_postfix}.json")
        output_file = os.path.join(output_dir,
            f"evaluation_{if_eval_with_gdth_hyp}_{model_name_eval}_{bkg_id_str}_{init_id_str}_{output_dir_postfix}.json")
        
        command = [
            PYTHON_EXECUTABLE, "-u", script,
            "--model_name", model_name_eval,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--chem_annotation_path", "./external/MC/Data/chem_research_2024.xlsx",
            "--corpus_size", "150",
            "--hypothesis_dir", hypothesis_file,
            "--output_dir", output_file,
            "--if_save", "1",
            "--if_load_from_saved", "0",
            "--if_with_gdth_hyp_annotation", str(if_eval_with_gdth_hyp),
            "--custom_inspiration_corpus_path", custom_inspiration_corpus_path
        ]
        
        run(command)
        output_files['evaluation'] = output_file
    
    print("\n" + "="*50)
    print("MC Pipeline Completed")
    print("="*50 + "\n")
    
    return output_files


def run_MC2(api_type, api_key, base_url, model_name_gene, model_name_eval, 
            custom_research_background_and_coarse_hyp_path, bkg_id, 
            output_dir_postfix, init_hyp_id):
    """
    Run MC2 pipeline with hierarchical greedy search.
    
    Args:
        api_type: API type (e.g., "openai")
        api_key: API key for the service
        base_url: Base URL for the API
        model_name_gene: Model name for hypothesis generation
        model_name_eval: Model name for hypothesis evaluation
        custom_research_background_and_coarse_hyp_path: Path to custom research background and coarse hypothesis
        bkg_id: Background ID
        output_dir_postfix: Postfix for output directory
        init_hyp_id: Initial hypothesis ID
    
    Returns:
        str: Path to the output file
    """
    
    # Configuration parameters (matching the bash script defaults)
    if_hierarchical = 1
    num_hierarchy = 5
    locam_minimum_threshold = 2
    if_multiple_llm = 1
    if_use_custom_research_background_and_coarse_hyp = 1
    beam_compare_mode = 0
    beam_size_branching = 2
    num_init_for_EU = 3
    num_recom_trial_for_better_hyp = 2
    if_feedback = 1
    if_parallel = 1
    if_use_vague_cg_hyp_as_input = 1
    if_generate_with_example = 1
    if_generate_with_past_failed_hyp = 0
    
    # Convert IDs to strings
    bkg_id_str = str(bkg_id) if bkg_id is not None else "0"
    init_hyp_id_str = str(init_hyp_id) if init_hyp_id is not None else "0"
    
    # Prepare output directory and file path
    checkpoint_dir = "./Checkpoints"
    output_dir = os.path.join(checkpoint_dir, output_dir_postfix) if output_dir_postfix else checkpoint_dir
    
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    print("\n" + "="*50)
    print("Running MC2 Hierarchical Greedy Search")
    print("="*50 + "\n")
    
    if if_hierarchical == 1:
        # Hierarchical greedy search
        script = os.path.join(BASE_DIR, "external", "MC2", "Method", "hierarchy_greedy.py")
        output_file = os.path.join(output_dir,
            f"hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_"
            f"{model_name_gene}_{model_name_eval}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_"
            f"num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_"
            f"if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_"
            f"if_generate_with_past_failed_hyp_{if_generate_with_past_failed_hyp}_"
            f"bkgid_{bkg_id_str}_init_hyp_id_{init_hyp_id_str}_{output_dir_postfix}.pkl"
        )
        
        command = [
            PYTHON_EXECUTABLE, "-u", script,
            "--bkg_id", "0",  # Set to 0 as per bash script comment
            "--api_type", api_type,
            "--api_key", api_key,
            "--eval_api_key", api_key,  # Using same key for eval
            "--base_url", base_url,
            "--model_name", model_name_gene,
            "--eval_model_name", model_name_eval,
            "--output_dir", output_file,
            "--if_save", "1",
            "--max_search_step", "150",
            "--locam_minimum_threshold", str(locam_minimum_threshold),
            "--if_feedback", str(if_feedback),
            "--num_hierarchy", str(num_hierarchy),
            "--beam_compare_mode", str(beam_compare_mode),
            "--beam_size_branching", str(beam_size_branching),
            "--num_init_for_EU", str(num_init_for_EU),
            "--num_recom_trial_for_better_hyp", str(num_recom_trial_for_better_hyp),
            "--if_parallel", str(if_parallel),
            "--if_multiple_llm", str(if_multiple_llm),
            "--if_use_vague_cg_hyp_as_input", str(if_use_vague_cg_hyp_as_input),
            "--if_generate_with_example", str(if_generate_with_example),
            "--if_generate_with_past_failed_hyp", str(if_generate_with_past_failed_hyp),
            "--if_use_custom_research_background_and_coarse_hyp", str(if_use_custom_research_background_and_coarse_hyp),
            "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path
        ]
    else:
        # Non-hierarchical greedy search
        script = os.path.join(BASE_DIR, "external", "MC2", "Method", "greedy.py")
        output_file = os.path.join(output_dir,
            f"greedy_{locam_minimum_threshold}_{if_feedback}_{model_name_gene}_{model_name_eval}_"
            f"if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_"
            f"if_generate_with_past_failed_hyp_{if_generate_with_past_failed_hyp}_"
            f"bkgid_{bkg_id_str}_init_hyp_id_{init_hyp_id_str}_{output_dir_postfix}.json"
        )
        
        command = [
            PYTHON_EXECUTABLE, "-u", script,
            "--bkg_id", "0",
            "--api_type", api_type,
            "--api_key", api_key,
            "--eval_api_key", api_key,
            "--base_url", base_url,
            "--model_name", model_name_gene,
            "--eval_model_name", model_name_eval,
            "--output_dir", output_file,
            "--if_save", "1",
            "--max_search_step", "150",
            "--locam_minimum_threshold", str(locam_minimum_threshold),
            "--if_feedback", str(if_feedback),
            "--if_multiple_llm", str(if_multiple_llm),
            "--if_use_vague_cg_hyp_as_input", str(if_use_vague_cg_hyp_as_input),
            "--if_generate_with_example", str(if_generate_with_example),
            "--if_generate_with_past_failed_hyp", str(if_generate_with_past_failed_hyp),
            "--if_use_custom_research_background_and_coarse_hyp", str(if_use_custom_research_background_and_coarse_hyp),
            "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path
        ]
    
    # Execute the command
    run(command)
    
    print("\n" + "="*50)
    print("MC2 Pipeline Completed")
    print("="*50 + "\n")
    
    return output_file