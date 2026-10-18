import pymupdf
from pathlib import Path

def create_sample_paper_pdf():
    output_dir = Path(__file__).resolve().parent / "sample_papers"
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_path = output_dir / "sample_postprandial_walk_study.pdf"

    doc = pymupdf.open()
    rect = pymupdf.Rect(40, 45, 555, 800)

    # Page 1: Title, Abstract, Introduction
    p1 = doc.new_page(width=595, height=842)
    text_p1 = """CLINICAL METABOLIC INVESTIGATION • ORIGINAL RESEARCH
Indian Journal of Clinical Metabolic Medicine • DOI: 10.1016/j.ijcmm.2024.08.012

Postprandial Glycemic Excursions and 10-Minute Post-Meal Walking in South Asian Adults with Prediabetes: A Randomized Crossover Study

Authors:
Dr. R. Ramanathan, MD, DM (Endocrinology)¹
Dr. A. Sundaram, PhD (Metabolic Physiology)²
Dr. Priya Venkatesh, MD (Preventive Medicine)¹

Affiliations:
¹ Center for Cardiometabolic Research, Chennai, India
² Metabolic Health Research Collaborative, Bengaluru, India

ABSTRACT
Background: South Asian populations exhibit accelerated transitions from insulin resistance to type 2 diabetes, driven in part by pronounced postprandial glucose excursions following carbohydrate-dense traditional diets. While formal aerobic exercise programs face severe adherence barriers among working adults, the metabolic efficacy of brief, low-intensity post-meal ambulation remains insufficiently characterized.
Methods: We conducted a randomized, four-condition crossover clinical trial involving 48 South Asian adults with diagnosed prediabetes (fasting glucose 100–125 mg/dL; HbA1c 5.7–6.4%; mean age 42.6 ± 6.2 years; 54% female). Participants consumed standardized Indian mixed meals (75g net carbohydrate equivalent: brown rice, dal, and cooked vegetables) followed by four distinct interventions: (A) Prolonged seated rest; (B) Immediate 10-minute walk starting 15 minutes postprandially; (C) Delayed 10-minute walk starting 60 minutes postprandially; and (D) 30-minute structured treadmill walking at 65% VO2max. Continuous glucose monitoring recorded interstitial glucose every 5 minutes for 180 minutes post-ingestion.
Results: A 10-minute post-meal walk initiated within 30 minutes of ingestion produced a 34% reduction in peak glucose elevation compared with sedentary rest (peak delta: 38.4 ± 6.2 mg/dL vs 58.1 ± 7.9 mg/dL, p < 0.001). When walking was postponed until 60 minutes postprandially, the reduction in blood glucose area under the curve diminished from 34% to 9%.
Conclusion: Immediate brief ambulation leverages skeletal muscle contraction to blunt glycemic spikes before hepatic glucose storage saturation occurs.

Keywords: Postprandial hyperglycemia; South Asian diabetes; Shatapadi; GLUT4 translocation; Continuous glucose monitoring; Prediabetes
"""
    p1.insert_textbox(rect, text_p1, fontsize=9, fontname="helv")

    # Page 2: Methods & Protocol
    p2 = doc.new_page(width=595, height=842)
    text_p2 = """METHODS AND EXPERIMENTAL PROTOCOL

Study Design and Ethical Approvals
The study protocol was approved by the Institutional Ethics Committee (IEC-CMR-2023-089) and conducted in strict adherence to the Declaration of Helsinki. Written informed consent was obtained from all 48 enrolled participants prior to baseline screening.

Participant Selection Criteria
Eligible participants were adults aged 30–55 years residing in Chennai and Bengaluru with clinical criteria for impaired fasting glucose or prediabetes defined by American Diabetes Association guidelines (HbA1c between 5.7% and 6.4%). Exclusion criteria included prior pharmacotherapy for hyperglycemia (metformin, sulfonylureas, or GLP-1 receptor agonists), severe cardiovascular disease, renal insufficiency, and active musculoskeletal impairments precluding gentle walking.

Standardized Test Meals
To evaluate real-world physiological responses, test meals replicated typical South Asian urban dietary composition. Each standardized lunch comprised 150g cooked Sona Masuri rice, 100g spiced lentil preparation (toor dal), 100g mixed vegetable sabzi, and 50g set curd. The macronutrient distribution was 68% carbohydrate, 14% protein, and 18% fat, providing 520 kcal with a standardized glycemic load of 42.

Intervention Protocols
Participants attended the metabolic laboratory on four separate mornings separated by 7-day washout intervals:
Condition A (Sedentary Control): Following meal consumption within a 15-minute window, participants remained comfortably seated in an ergonomic desk chair for 180 minutes, engaging in low-cognitive computer tasks without ambulation.
Condition B (Early Brief Ambulation): Exactly 15 minutes after the final bite, subjects stood and walked at a relaxed pace (3.0 km/h; equivalent to ~75 steps per minute) along a climate-controlled indoor corridor for exactly 10 minutes. Following the walk, they remained seated for the balance of the 180-minute trial.
Condition C (Delayed Ambulation): Subjects sat for 60 minutes post-meal, then performed an identical 10-minute walk at 3.0 km/h, returning to sit thereafter.
Condition D (Standard Aerobic Session): Subjects remained seated for 30 minutes, then completed 30 minutes of brisk treadmill walking at 5.5 km/h with 1% incline.
"""
    p2.insert_textbox(rect, text_p2, fontsize=9.5, fontname="helv")

    # Page 3: Results & Physiological Mechanisms
    p3 = doc.new_page(width=595, height=842)
    text_p3 = """RESULTS

Glycemic Excursions and Continuous Sensor Trajectories
Primary endpoint analysis demonstrated profound attenuation of postprandial glucose excursions during early brief ambulation.
Under Condition A (sedentary rest), mean interstitial glucose climbed from a fasting baseline of 108.2 ± 8.4 mg/dL to a peak postprandial value of 166.3 ± 14.1 mg/dL at 45 minutes post-ingestion.

In contrast, Condition B (10-minute walk at 15 minutes) dramatically suppressed the ascending limb of the glucose curve. Peak interstitial glucose reached only 146.6 ± 11.2 mg/dL.
A 10-minute post-meal walk initiated within 30 minutes of ingestion produced a 34% reduction in peak glucose elevation compared with sedentary rest (p < 0.001).

TABLE 1: Glycemic Parameters across Experimental Conditions (n=48)
---------------------------------------------------------------------------------------------------
Parameter                                Condition A (Rest)    Condition B (10m Walk)    Condition C (Delayed)
---------------------------------------------------------------------------------------------------
Baseline Fasting (mg/dL)                 108.2 ± 8.4           107.9 ± 7.9               108.5 ± 8.1
Peak Glucose Concentration (mg/dL)       166.3 ± 14.1          146.6 ± 11.2              161.4 ± 13.8
Net Peak Elevation (delta mg/dL)         58.1 ± 7.9            38.4 ± 6.2 (-34%)         52.9 ± 7.4 (-9%)
Incremental AUC 0-180m (mg·min/dL)       4,120 ± 620           2,680 ± 440 (-35%)        3,790 ± 580 (-8%)
Time to Return to Baseline (min)         145 ± 18              82 ± 12                   132 ± 16
---------------------------------------------------------------------------------------------------

Cellular Mechanism: Non-Insulin Glucose Clearance
Skeletal muscle contractions during light ambulation facilitate GLUT4 translocation independent of insulin signaling pathways.
During resting postprandial states, glucose uptake depends primarily on insulin receptor tyrosine kinase activation, which is chronically impaired in insulin-resistant individuals. However, mechanical tension generated by the quadriceps and soleus activates 5' AMP-activated protein kinase (AMPK) and calcium/calmodulin-dependent protein kinase II (CaMKII). These signals trigger translocation of intracellular GLUT4 storage vesicles directly to the muscle sarcolemma, clearing glucose directly from the bloodstream without imposing secretory burdens on pancreatic beta cells.
"""
    p3.insert_textbox(rect, text_p3, fontsize=9, fontname="helv")

    # Page 4: Discussion, Timing, Limitations
    p4 = doc.new_page(width=595, height=842)
    text_p4 = """DISCUSSION AND TIMING CHRONOBIOLOGY

The Importance of the Immediate Post-Meal Window
Our findings underscore the physiological criticality of movement timing. In modern urban lifestyles, the natural instinct following dinner is sedentary leisure—collapsing onto a sofa or viewing screens. This sedentary inertia coincides precisely with maximal rate of gastric emptying and splanchnic glucose absorption (typically occurring 20–45 minutes postprandially).

When walking was postponed until 60 minutes postprandially, the reduction in blood glucose area under the curve diminished from 34% to 9%.
By 60 minutes, the vast majority of dietary glucose has already entered circulation, stimulating supranormal compensatory insulin hypersecretion. The delayed movement occurs after peak endothelial shear stress and oxidative stress from the glycemic surge have already inflicted vascular insult.

Traditional Cultural Resonance: The Practice of Shatapadi
Interestingly, these physiological discoveries provide empirical validation for the ancient Indian Ayurvedic habit known as 'Shatapadi' (literally: taking 100 paces after eating). Rather than demanding rigorous, intimidating fitness regimens that experience over 80% attrition within 3 months, prescribing a 10-minute relaxed stroll leverages cultural familiarity and achievable behavioral design.

Study Limitations
Several important limitations must be noted:
1. Short-term observation: Our protocol evaluated acute postprandial excursions over 7-day intervals; long-term randomized clinical trials over 12–24 months are required to quantify sustained reductions in HbA1c and visceral adiposity.
2. Standardized test meal: While the meal reflected typical South Asian carbohydrate density, real-world variations including festive celebrations, deep-fried snacks (namkeen/samosas), and high-fat gravies may alter gastric emptying rates.
3. Cohort characteristics: The study enrolled non-pregnant adult subjects with prediabetes; outcomes cannot be generalized directly to individuals with established insulin-dependent Type 1 diabetes.
"""
    p4.insert_textbox(rect, text_p4, fontsize=9, fontname="helv")

    # Page 5: Conclusions & References
    p5 = doc.new_page(width=595, height=842)
    text_p5 = """CONCLUSION AND CLINICAL RECOMMENDATIONS

In South Asian adults with prediabetes, a gentle 10-minute post-meal walk initiated within 15–30 minutes of eating significantly blunts peak glycemic excursions by 34% through insulin-independent GLUT4 transporter translocation. Delaying movement beyond 60 minutes renders the habit less than one-third as effective. Clinicians treating metabolic dysfunction in India should prescribe immediate post-meal pacing as a foundational, non-pharmacological habit.

AUTHORS' CONTRIBUTIONS
RR conceived the study, supervised clinical trials, and drafted the manuscript. AS conducted metabolic modeling and statistical analysis. PV managed continuous glucose monitoring sensors and patient safety monitoring. All authors reviewed and approved the final manuscript.

FUNDING AND COMPETING INTERESTS
This research was supported by the Indian Metabolic Research Initiative Grant (IMRI-2023-41). The authors declare no competing financial or commercial conflicts of interest.

REFERENCES
1. Mohan V, et al. Mortality and cardiovascular disease in South Asians with prediabetes: The ICMR-INDIAB population study. Lancet Diabetes Endocrinol. 2022;10(8):573-582.
2. Reynolds AN, et al. Advice to walk after meals is more effective for glycemic control than advice to walk at any time: A randomized crossover trial. Diabetologia. 2016;59(12):2572-2578.
3. Richter EA, Hargreaves M. Exercise, GLUT4 translocation and skeletal muscle glucose uptake. Physiol Rev. 2013;93(3):993-1017.
4. Anjana RM, et al. Prevalence of diabetes and prediabetes in India: A statewide analysis of the ICMR-INDIAB study. Lancet Diabetes Endocrinol. 2023;11(7):474-489.
5. Colberg SR, et al. Physical activity/exercise and diabetes: A position statement of the American Diabetes Association. Diabetes Care. 2016;39(11):2065-2079.
"""
    p5.insert_textbox(rect, text_p5, fontsize=9.5, fontname="helv")

    doc.save(str(pdf_path))
    doc.close()
    print(f"Generated sample paper at: {pdf_path}")
    return pdf_path

if __name__ == "__main__":
    create_sample_paper_pdf()
