import pymupdf as fitz
from pathlib import Path

def create_sample_paper():
    out_path = Path("sample_papers/stamatakis_vilpa_nature_med_2022.pdf")
    out_path.parent.mkdir(parents=True, exist_ok=True)

    doc = fitz.open()

    # --- PAGE 1 ---
    page1 = doc.new_page(width=595, height=842) # A4
    text_p1 = """Association of wearable device-measured vigorous intermittent lifestyle physical activity with mortality
Emmanuel Stamatakis, Matthew N. Ahmadi, Jason M. R. Gill, Sebastien Chastin, Mark Hamer
Nature Medicine, Volume 28, pages 2521-2529 (December 2022)
DOI: 10.1038/s41591-022-02100-x

ABSTRACT
Vigorous physical activity is an efficient way to achieve physical fitness, but participation in structured exercise is low among middle-aged and older adults. Vigorous intermittent lifestyle physical activity (VILPA) refers to brief and sporadic bouts (e.g., up to 1 to 2 minutes) of vigorous physical activity during daily life. Here, we examined the association of accelerometer-measured VILPA with all-cause, cardiovascular disease (CVD), and cancer mortality in 25,241 non-exercisers (mean age 61.8 years, 56.2% female) from the UK Biobank over a mean follow-up of 6.9 years.

INTRODUCTION
Physical inactivity remains a global pandemic contributing to substantial morbidity and premature mortality. While guideline-recommended physical activity typically requires 150 to 300 minutes per week of moderate-intensity activity or 75 to 150 minutes of vigorous activity, fewer than 20% of adults regularly engage in leisure-time exercise. Understanding whether short bouts of incidental physical activity—such as power walking during a commute, carrying groceries, or climbing stairs—provide cardioprotective benefits is vital for population-scale health guidelines.

METHODS & COHORT CHARACTERISTICS
The study cohort comprised 25,241 participants from the UK Biobank who reported no structured exercise participation and wore a wrist-worn Axivity AX3 triaxial accelerometer continuously for 7 days. Accelerometer data were sampled at 100 Hz and calibrated to gravitational units. VILPA bouts were defined as continuous vigorous movement of up to 1 or 2 minutes duration. The primary outcomes were all-cause mortality, cardiovascular disease mortality, and total cancer mortality, ascertained through linkage to national death registers.
"""
    rect1 = fitz.Rect(50, 50, 545, 800)
    page1.insert_textbox(rect1, text_p1, fontsize=10, fontname="helv")

    # --- PAGE 2 ---
    page2 = doc.new_page(width=595, height=842)
    text_p2 = """RESULTS & MEASUREMENTS
During a mean follow-up of 6.9 years (174,166 person-years), 852 deaths were recorded, including 266 cardiovascular deaths and 511 cancer deaths. Among non-exercisers, the median duration of daily VILPA was 4.0 minutes per day across approximately 3 bouts.

Primary Quantitative Findings:
1. In participants engaging in a minimum of 3 to 4 bouts of VILPA per day (lasting approximately 1 to 2 minutes each), all-cause and cancer mortality risk was reduced by 38% to 40% (hazard ratio HR = 0.60; 95% CI: 0.50-0.73; p < 0.001) compared with individuals recording zero VILPA.
2. Cardiovascular disease (CVD) mortality demonstrated an even steeper inverse dose-response relationship: participants recording 3 bouts of VILPA per day exhibited a 48% to 49% reduction in CVD mortality risk (HR = 0.51; 95% CI: 0.35-0.74; p = 0.001).
3. The near-maximal risk reduction was observed at 11 bouts per day, which was associated with a 65% reduction in cardiovascular disease mortality risk (HR = 0.35; 95% CI: 0.23-0.54) and a 49% reduction in cancer mortality risk.

Table 1: Hazard Ratios for Mortality by Daily VILPA Bouts in Non-Exercisers (n=25,241)
- Bouts per day: 0 bouts (Reference, HR = 1.00)
- Bouts per day: 1-2 bouts (HR = 0.82; 95% CI: 0.71-0.95)
- Bouts per day: 3-4 bouts (HR = 0.60; 95% CI: 0.50-0.73)
- Bouts per day: 5-7 bouts (HR = 0.52; 95% CI: 0.41-0.67)
- Bouts per day: 8-11 bouts (HR = 0.44; 95% CI: 0.32-0.59)
"""
    rect2 = fitz.Rect(50, 50, 545, 800)
    page2.insert_textbox(rect2, text_p2, fontsize=10, fontname="helv")

    # --- PAGE 3 ---
    page3 = doc.new_page(width=595, height=842)
    text_p3 = """DISCUSSION & PHYSIOLOGICAL MECHANISMS
These findings indicate that small amounts of vigorous intermittent physical activity accumulated during daily living are associated with substantially lower premature mortality. Intermittent vigorous bursts trigger rapid cardiorespiratory stimulus, enhancing arterial compliance, improving endothelial nitric oxide release, and upregulating insulin-dependent GLUT4 translocation in skeletal muscle cells within minutes.

LIMITATIONS & UNCERTAINTIES
Several methodological caveats must be emphasized:
1. Observational Design: Although analyses excluded individuals with baseline cardiovascular events and deaths occurring within the first 2 years of follow-up to mitigate reverse causation, residual confounding remains possible.
2. Measurement Window: Accelerometry was recorded over a single 7-day period at baseline, which may not capture seasonal variations or lifetime physical activity trajectories.
3. Population Bounds: The UK Biobank sample is predominantly of European descent and healthier than the general UK population, limiting immediate generalizability to multi-ethnic populations with different baseline cardiovascular comorbidities.
4. Relative vs. Absolute Risk: The 48% reduction in cardiovascular mortality represents a relative risk reduction; absolute risk differences depend heavily on individual baseline cardiovascular health and age.

CONCLUSION
Engaging in as little as 3 to 4 one-minute bouts of vigorous intermittent physical activity daily is associated with clinically meaningful reductions in cardiovascular and cancer mortality. These findings offer an accessible health target for adults unable or unwilling to participate in structured exercise routines.
"""
    rect3 = fitz.Rect(50, 50, 545, 800)
    page3.insert_textbox(rect3, text_p3, fontsize=10, fontname="helv")

    doc.save(str(out_path))
    doc.close()
    print(f"Sample paper generated at: {out_path} ({out_path.stat().st_size} bytes)")

if __name__ == "__main__":
    create_sample_paper()
