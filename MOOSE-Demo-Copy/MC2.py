import os
import subprocess
import argparse
import sys


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PYTHON_EXECUTABLE = sys.executable

# def run(command_list):
#     command_list = [str(x) for x in command_list]
#     print("Running:", " ".join(command_list))
#     subprocess.run(command_list, check=True)
def run(command_list):
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
        print(
            "---------------------------BBBBBBBBBCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC---------------------------")

        for line in process.stdout:
            print(line, end='')
    except KeyboardInterrupt:
        print(
            "---------------------------CCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCCC---------------------------")
        print("\nKeyboardInterrupt received, terminating process...")
        process.terminate()
        process.wait()
        raise
    finally:
        process.stdout.close()

    return_code = process.wait()
    if return_code != 0:
        raise subprocess.CalledProcessError(return_code, command_list)


def run_mc2_pipeline(
    api_type, api_key, base_url,
    model_name, eval_model_name,
    custom_research_background_and_coarse_hyp_path,
    function_mode,
    bkg_id=None,
    output_dir_postfix=None,
    init_hyp_id=None
):
    checkpoint_dir = "./Checkpoints"
    output_dir = os.path.join(checkpoint_dir, output_dir_postfix) if output_dir_postfix else "./Checkpoints"

    if function_mode == 0:
        if_hierarchical = 1
        num_hierarchy = 5
        locam_minimum_threshold = 2
        if_multiple_llm = 1
        if_use_custom_input = 1
        beam_compare_mode = 0
        beam_size_branching = 2
        num_init_for_EU = 3
        num_recom_trial_for_better_hyp = 2
        if_feedback = 1
        if_parallel = 1
        if_use_vague_cg_hyp_as_input = 1
        if_generate_with_example = 1

        bkg_id_str = str(bkg_id) if bkg_id is not None else "0"
        init_hyp_id_str = str(init_hyp_id) if init_hyp_id is not None else "0"

        if if_hierarchical == 0:
            script = os.path.join(BASE_DIR, "external", "MC2", "Method", "greedy.py")
            output_file = os.path.join(output_dir,
                f"greedy_{locam_minimum_threshold}_{if_feedback}_{model_name}_{eval_model_name}_"
                f"if_multiple_llm_{if_multiple_llm}_if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_"
                f"bkgid_{bkg_id_str}_init_hyp_id_{init_hyp_id_str}_{output_dir_postfix}.json"
            )
        else:
            script = os.path.join(BASE_DIR, "external", "MC2", "Method", "hierarchy_greedy.py")
            output_file = os.path.join(output_dir,
                f"hierarchical_greedy_{num_hierarchy}_{locam_minimum_threshold}_{if_feedback}_{num_recom_trial_for_better_hyp}_"
                f"{model_name}_{eval_model_name}_beam_compare_mode_{beam_compare_mode}_beam_size_branching_{beam_size_branching}_"
                f"num_init_for_EU_{num_init_for_EU}_if_multiple_llm_{if_multiple_llm}_"
                f"if_use_vague_cg_hyp_as_input_{if_use_vague_cg_hyp_as_input}_"
                f"bkgid_{bkg_id_str}_init_hyp_id_{init_hyp_id_str}_{output_dir_postfix}.pkl"
            )

        run([
            PYTHON_EXECUTABLE, "-u", script,
            "--bkg_id", "0",
            "--api_type", api_type,
            "--api_key", api_key,
            "--eval_api_key", api_key,
            "--base_url", base_url,
            "--model_name", model_name,
            "--eval_model_name", eval_model_name,
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
            "--if_use_custom_research_background_and_coarse_hyp", str(if_use_custom_input),
            "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path
        ])

    elif function_mode == 1:
        run([
            PYTHON_EXECUTABLE, "-u", "Evaluation/pairwise_compare.py",
            "--model_name", model_name,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--eval_example_path", "./Checkpoints/Backup/eval_example.json"
        ])

    elif function_mode == 2:
        run([
            PYTHON_EXECUTABLE, "-u", "Evaluation/evaluate.py",
            "--model_name", model_name,
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--preprocess_groundtruth_components_dir", "./Checkpoints/groundtruth_hyp_components_collection.json",
            "--num_compare_times", "5"
        ])

    elif function_mode == 3:
        run([
            PYTHON_EXECUTABLE, "-u", "Evaluation/analysis.py",
            "--api_type", api_type,
            "--api_key", api_key,
            "--base_url", base_url,
            "--preprocess_groundtruth_components_dir", "./Checkpoints/groundtruth_hyp_components_collection.json"
        ])

    elif function_mode == 4:
        run([
            PYTHON_EXECUTABLE, "-u", "Preprocessing/input_hyp_processing.py",
            "--model_name", model_name,
            "--api_key", api_key,
            "--base_url", base_url,
            "--output_dir", "./Data/processed_research_direction.json"
        ])

    elif function_mode == 5:
        run([
            PYTHON_EXECUTABLE, "-u", "Preprocessing/custom_research_background_dumping.py",
            "--if_load_from_moosechem_ranking_file", "1",
            "--moosechem_ranking_file_path", "~/MOOSE-Chem/Geo/evaluation_GPT4o-mini.json",
            "--custom_research_background_and_coarse_hyp_path", custom_research_background_and_coarse_hyp_path
        ])

    elif function_mode == 6:
        run([
            PYTHON_EXECUTABLE, "-u", "Preprocessing/display_hypothesis.py",
            "--if_hierarchical", "1",
            "--hierarchy_id", "4",
            "--start_bkg_id", "0",
            "--end_bkg_id", "4",
            "--display_txt_file_path", "./finegrained_hyp.txt"
        ])


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("api_type")
    parser.add_argument("api_key")
    parser.add_argument("base_url")
    parser.add_argument("model_name")
    parser.add_argument("eval_model_name")
    parser.add_argument("custom_research_background_and_coarse_hyp_path")
    parser.add_argument("function_mode", type=int)
    parser.add_argument("--bkg_id", default="0")
    parser.add_argument("--output_dir_postfix", default="default")
    parser.add_argument("--init_hyp_id", default="0")

    args = parser.parse_args()

    run_mc2_pipeline(
        args.api_type,
        args.api_key,
        args.base_url,
        args.model_name,
        args.eval_model_name,
        args.custom_research_background_and_coarse_hyp_path,
        args.function_mode,
        args.bkg_id,
        args.output_dir_postfix,
        args.init_hyp_id
    )
