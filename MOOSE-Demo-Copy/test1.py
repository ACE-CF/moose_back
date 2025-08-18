import Utils.demo_utils as utils
from MooseDemo import MooseDemo

# api_type: 0 (openai) or 1 (azure)
# api_key / base_url: input from user
# model_name: input from user
job_name = "job_name1"  # e.g., "baseline_MC"; use a unique name to avoid overwriting results
moose_demo = MooseDemo(0,"sk-nD59p1EN85wAVXv9AMQCWbib1LOlJ35aIwun5e7JJ3rSJHlA", "http://35.220.164.252:3888/v1/", "gpt-4o-mini", "job_name1")

research_question = "your research question"
background_survey = "your literature survey"
print("round 1")
moose_demo.write_MC_start_file_research_background(research_question, background_survey)
raw_insp_xlsx_dir = f"./StartFiles/{job_name}"
moose_demo.write_MC_start_file_inspiration_corpus(raw_insp_xlsx_dir,0)
print("round 2")
which_stage = [1, 0, 0]  # [inspiration, composition, ranking]
moose_demo.run_MC(which_stage)
which_stage = [0, 1, 0]
moose_demo.run_MC(which_stage)
which_stage = [0, 0, 1]
moose_demo.run_MC(which_stage)