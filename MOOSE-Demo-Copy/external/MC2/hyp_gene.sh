#!/bin/bash
#SBATCH -J test
#SBATCH -o logs/test.out 
#SBATCH -e logs/test.out  
#SBATCH -p PA100q        
#SBATCH -N 1               
#SBATCH -n 1               
#SBATCH --gres=gpu:0


if_hierarchical=1
num_hierarchy=5
locam_minimum_threshold=2

beam_compare_mode=0
beam_size_branching=2
num_init_for_EU=3
num_recom_trial_for_better_hyp=2
if_feedback=1
if_parallel=1
if_use_vague_cg_hyp_as_input=1
if_generate_with_example=1
if_generate_with_past_failed_hyp=1
if_multiple_llm=1


model_name=gpt-4o-mini
eval_model_name=gpt-4o-mini
api_key=sk-nD59p1EN85wAVXv9AMQCWbib1LOlJ35aIwun5e7JJ3rSJHlA
eval_api_key=sk-nD59p1EN85wAVXv9AMQCWbib1LOlJ35aIwun5e7JJ3rSJHlA
base_url=http://35.220.164.252:3888/v1/
# updated_prompt_feb_14 / updated_prompt_mar_29 / test
output_dir_postfix="updated_prompt_mar_29"
if_use_custom_research_background_and_coarse_hyp=0
custom_research_background_and_coarse_hyp_path=./custom_research_background_and_coarse_hyp.json



# for bkg_id in {0..10}
# for bkg_id in {11..20}/
# for bkg_id in {21..30}
# for bkg_id in {31..40}
# for bkg_id in {41..50}
# for bkg_id in {0..4}
# for bkg_id in {5..9}
# for bkg_id in {10..14}
# for bkg_id in {15..19}
# for bkg_id in {20..23}
# for bkg_id in {24..26}
# for bkg_id in {27..29}
# for bkg_id in {30..32}
# for bkg_id in {33..35}
# for bkg_id in {36..40}
# for bkg_id in {41..44}
# for bkg_id in {45..48}
# for bkg_id in {49..50}
for bkg_id in {9..9}
do 
    echo "\n\nEntering loop for bkg_id: $bkg_id"
    ## framework inference
    if [[ ${if_hierarchical} -eq 0 ]]; then
        python -u ./Method/greedy.py \
            --bkg_id ${bkg_id} \
            --api_type 0 --api_key ${api_key} --eval_api_key ${eval_api_key} --base_url ${base_url} \
            --model_name ${model_name} --eval_model_name ${eval_model_name} \
            --output_dir ./Checkpoints/greedy_${locam_minimum_threshold}_${if_feedback}_${model_name}_${eval_model_name}_if_multiple_llm_${if_multiple_llm}_if_use_vague_cg_hyp_as_input_${if_use_vague_cg_hyp_as_input}_if_generate_with_past_failed_hyp_${if_generate_with_past_failed_hyp}_bkgid_${bkg_id}_${output_dir_postfix}.json \
            --if_save 1 \
            --max_search_step 150 --locam_minimum_threshold ${locam_minimum_threshold} --if_feedback ${if_feedback} \
            --if_multiple_llm ${if_multiple_llm} --if_use_vague_cg_hyp_as_input ${if_use_vague_cg_hyp_as_input} --if_generate_with_example ${if_generate_with_example} \
            --if_generate_with_past_failed_hyp ${if_generate_with_past_failed_hyp} \
            --if_use_custom_research_background_and_coarse_hyp ${if_use_custom_research_background_and_coarse_hyp} \
            --custom_research_background_and_coarse_hyp_path ${custom_research_background_and_coarse_hyp_path} 
    elif [[ ${if_hierarchical} -eq 1 ]]; then
        python -u ./Method/hierarchy_greedy.py \
            --bkg_id ${bkg_id} \
            --api_type 0 --api_key ${api_key} --eval_api_key ${eval_api_key} --base_url ${base_url} \
            --model_name ${model_name} --eval_model_name ${eval_model_name} \
            --output_dir ./Checkpoints/hierarchical_greedy_${num_hierarchy}_${locam_minimum_threshold}_${if_feedback}_${num_recom_trial_for_better_hyp}_${model_name}_${eval_model_name}_beam_compare_mode_${beam_compare_mode}_beam_size_branching_${beam_size_branching}_num_init_for_EU_${num_init_for_EU}_if_multiple_llm_${if_multiple_llm}_if_use_vague_cg_hyp_as_input_${if_use_vague_cg_hyp_as_input}_if_generate_with_past_failed_hyp_${if_generate_with_past_failed_hyp}_bkgid_${bkg_id}_${output_dir_postfix}.pkl \
            --if_save 1 \
            --max_search_step 150 --locam_minimum_threshold ${locam_minimum_threshold} --if_feedback ${if_feedback} \
            --num_hierarchy ${num_hierarchy} --beam_compare_mode ${beam_compare_mode} --beam_size_branching ${beam_size_branching} \
            --num_init_for_EU ${num_init_for_EU} --num_recom_trial_for_better_hyp ${num_recom_trial_for_better_hyp} --if_parallel ${if_parallel} \
            --if_multiple_llm ${if_multiple_llm} --if_use_vague_cg_hyp_as_input ${if_use_vague_cg_hyp_as_input} --if_generate_with_example ${if_generate_with_example} \
            --if_generate_with_past_failed_hyp ${if_generate_with_past_failed_hyp} \
            --if_use_custom_research_background_and_coarse_hyp ${if_use_custom_research_background_and_coarse_hyp} \
            --custom_research_background_and_coarse_hyp_path ${custom_research_background_and_coarse_hyp_path} 
    fi
done