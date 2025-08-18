import os, sys, re
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from external.MC2.Method.utils import load_chem_annotation
from demo_utils import gdth_insp_keyword_to_text, write_MC_start_file, write_MC2_start_file, run_MC, run_MC2, load_MC_gene_hypothesis, load_MC2_gene_hypothesis, provide_feedback, demo_instruction_prompts


def test_gdth_insp_keyword_to_text():
    bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")

    cnt_insp = 0
    for cur_q in bkg_q:
        cur_note = dict_bkg2note[cur_q]
        insp_list, insp_prompt = gdth_insp_keyword_to_text(cur_note)
        cnt_insp += len(insp_list)
        print("inspiration list:", insp_list)
    print("cnt_insp:", cnt_insp)


# test_gdth_insp_keyword_to_text()


def text_write_MC_start_file():
    bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")
    research_question = bkg_q[0]
    background_survey = dict_bkg2survey[research_question]
    custom_research_background_path = "custom_research_background.json"
    write_MC_start_file(research_question, background_survey, custom_research_background_path)

# text_write_MC_start_file()


def test_write_MC2_start_file():
    bkg_q, dict_bkg2survey, dict_bkg2groundtruthHyp, dict_bkg2fg_hyp, dict_bkg2fg_exp, dict_bkg2note = load_chem_annotation("external/MC2/Data/chem_research_2024_finegrained.xlsx")
    research_question = bkg_q[0]
    background_survey = dict_bkg2survey[research_question]
    coarse_grained_hypothesis = dict_bkg2groundtruthHyp[research_question]
    custom_research_background_and_coarse_hyp_path = "custom_research_background_and_coarse_hyp.json"
    write_MC2_start_file(research_question, background_survey, coarse_grained_hypothesis, custom_research_background_and_coarse_hyp_path)

# test_write_MC2_start_file()


def test_run_MC():
    api_type = 1
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name_insp_retrieval = "GPT4o-mini"
    model_name_gene = "GPT4o-mini"
    model_name_eval = "GPT4o-mini"
    custom_research_background_path = "custom_research_background.json"
    custom_inspiration_corpus_path = "./external/MC/Data/Inspiration_Corpus_150.json"
    which_stage = [1, 1, 1]  # Perform all stages: inspiration retrieval, hypothesis composition, hypothesis ranking
    bkg_id = 0
    output_dir_postfix = "test_output1"
    run_MC(api_type, api_key, base_url, model_name_insp_retrieval, model_name_gene, model_name_eval,
           custom_research_background_path, custom_inspiration_corpus_path, which_stage, bkg_id, output_dir_postfix)
    

# test_run_MC()



def test_run_MC2():
    api_type = 1
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name_gene = "GPT4o-mini"
    model_name_eval = "GPT4o-mini"
    custom_research_background_and_coarse_hyp_path = "custom_research_background_and_coarse_hyp.json"
    output_dir_postfix = "test_output"
    run_MC2(api_type, api_key, base_url, model_name_gene, model_name_eval,
            custom_research_background_and_coarse_hyp_path, output_dir_postfix)
    
# test_run_MC2()



def test_load_MC_gene_hypothesis():

    model_name_eval = "GPT4o-mini"
    output_dir_postfix = "test_output"

    research_question, gene_hyp_list = load_MC_gene_hypothesis(output_dir_postfix, model_name_eval)
    print("Research Question:", research_question)
    for cur_hyp in gene_hyp_list:
        print("Gene Hypothesis:", cur_hyp[0])
        # print("Score:", cur_hyp[1])
        # print("Score list:", cur_hyp[2])

# test_load_MC_gene_hypothesis()


def test_load_MC2_gene_hypothesis():

    output_dir_postfix = "updated_prompt_feb_14"
    cur_bkg_hypothesis = load_MC2_gene_hypothesis(output_dir_postfix)
    print("Coarse-Grained Hypothesis:", cur_bkg_hypothesis)
    print("len(cur_bkg_hypothesis):", len(cur_bkg_hypothesis))

# test_load_MC2_gene_hypothesis()


def test_provide_feedback():
    api_type = 1
    api_key = os.getenv("API_KEY")
    base_url = os.getenv("BASE_URL")
    model_name = "GPT4o-mini"

    question = "How can we design a flexible thermogalvanic device that simultaneously maximizes both Carnot-relative efficiency and mechanical robustness for sustainable energy harvesting from body heat?"
    gene_hyp = "We hypothesize that the development of a flexible thermogalvanic device can be achieved through the innovative integration of an anisotropic hydrogel layer, synthesized via a controlled freeze-casting process, coupled with a dynamic thermal management layer composed of aligned silver nanowire networks, incorporating phase change materials (PCMs) to enhance heat dissipation.\n\nThe proposed methodology includes the following detailed steps:\n\n1. Electrolyte Development and Characterization: We will systematically investigate the solvent compositions for the electrolyte, particularly the ratios of water to acetone (0:100, 25:75, 50:50, 75:25, 100:0) and sodium chloride concentrations (0.1 M to 1.0 M), backed by previous literature indicating optimal thermopower outcomes at specific compositions. In addition to measuring the effective thermopower (\u03b1), we will assess viscosity, ion exchange rates, and thermal stability of the electrolytes to provide comprehensive data on their performance.\n\n2. Anisotropic Hydrogel Fabrication: We will synthesize anisotropic hydrogels using poly(vinyl alcohol) (PVA) with freeze-casting at cooling rates of 2 \u00b0C/min and freeze durations of 24 hours. The hydrogel formulation will include a calculated ionic conductive filler concentration of 15% by weight polyethylene oxide (PEO) to boost ionic conductivity. The microstructures will be characterized using scanning electron microscopy (SEM) and confirmed against targeted conductivity benchmarks of ~10 mS/cm.\n\n3. Dynamic Thermal Management Layer Design: The thermal management layer will be fabricated through a layered casting process, featuring aligned silver nanowire networks (10% by weight) integrated with phase change materials (e.g., paraffin wax) to ensure maximal thermal conductivity while maintaining a low profile. This approach ensures efficient heat dissipation and a robust interface with the hydrogel layer.\n\n4. Interface Optimization: We will apply a thermally conductive epoxy adhesive (e.g., EPOXY 550) with a calibrated thickness of 100 \u00b5m to bond the hydrogel and thermal management layers. This thickness choice will be justified based on established literature regarding the trade-off between bond strength and thermal contact resistance, ensuring minimal thermal resistance at the interface.\n\n5. Comprehensive Performance Evaluation: The mechanical properties of the device will adhere to ASTM standards, including D638 for tensile strength and D7791 for cyclic fatigue tests, establishing benchmarks of tensile strength \u2265 20 MPa and fatigue resistance > 10,000 cycles. Thermoelectric performance will be rigorously quantified using standardized measurements (laser flash analysis for thermal conductivity and four-point probe measurements for ionic conductivity) to validate the expected characteristics of the developed system.\n\n6. Risk Assessment and Scalability Considerations: Potential challenges in achieving consistent freeze-casting conditions and alignment of silver nanowires will be identified, along with contingencies to address these issues. Preliminary studies will explore the feasibility of scaling up the electrospinning and freeze-casting processes for larger production runs while maintaining material uniformity and performance consistency.\n\nBy systematically optimizing solvent compositions and integrating structural enhancements, this refined hypothesis aims to advance the design of flexible thermogalvanic devices, reinforcing their viability for sustainable energy harvesting applications while maintaining clarity and reproducibility across all methodological steps."
    gdth_hyp = "By integrating guanidine sulfate (Gdm)2SO4 into a poly(vinyl alcohol) (PVA) hydrogel and employing directional freezing to create aligned channels, it is possible to achieve a flexible thermogalvanic armor (FTGA) with a Carnot-relative efficiency exceeding 8% while maintaining high mechanical strength. This integration allows for enhanced thermopower and mechanical robustness, exceeding the performance of traditional quasi-solid thermocells."

    feedback = provide_feedback(question, gene_hyp, gdth_hyp, api_type, api_key, base_url, model_name)

    print("Feedback:", feedback)

test_provide_feedback()