

# job_name: baseline_MC, MC_with_hint, MC_with_feedback_with_hint, MC_with_feedback_stronger_with_hint, 
#               MC2_with_MC_input_self_rank, MC2_with_MC_input_oracle_rank, 
#               MC2_with_feedback_oracle_rank, MC2_with_feedback_x2_oracle_rank, MC2_with_feedback_x3_oracle_rank, MC2_with_feedback_x4_oracle_rank
#               MC2_with_feedback_x2_oracle_rank_only_1_feedback
#               MC2_with_feedback_v2_x2_oracle_rank
# MC_hyp_selection_method: best_self_eval, best_recall
python -u demo_exp.py \
        --job_name MC2_with_feedback_v2_x2_oracle_rank --prev_job_name MC2_with_feedback_oracle_rank --select_hyp_from_ckpt_method best_recall \
        --if_eval_with_gdth_hyp 1 --if_save 1 \
        --start_id 6 --end_id 10 \
        --clean_up_survey_from_first_selected_hyp_and_feedback 0 \
        --feedback_strength_level 2 \
        --api_type ${API_TYPE} --api_key "${API_KEY}" --base_url "${BASE_URL}" --model_name "${MODEL_NAME}" \
        # --api_type_eval ${API_TYPE_EVAL} --api_key_eval "${API_KEY_EVAL}" --base_url_eval "${BASE_URL_EVAL}" --model_name_eval "${MODEL_NAME_EVAL}" \



# Thermocell_simple, Thermocell_extensive
# python -u demo_exp.py \
#         --job_name Thermocell_simple \
#         --api_type ${API_TYPE} --api_key "${API_KEY}" --base_url "${BASE_URL}" --model_name "${MODEL_NAME}" \
#         --api_type_eval ${API_TYPE_EVAL} --api_key_eval "${API_KEY_EVAL}" --base_url_eval "${BASE_URL_EVAL}" --model_name_eval "${MODEL_NAME_EVAL}" \