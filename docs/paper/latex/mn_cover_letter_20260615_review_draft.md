# Cover Letter Draft for Review

Date: June 15, 2026

To the Editor-in-Chief and Editorial Office  
Microsystems & Nanoengineering

Dear Editor-in-Chief,

We wish to submit our original Article entitled "On-Board Real-Time AI Compensation System for Nonlinear Drift in Electrochemical Seismometers" for consideration in *Microsystems & Nanoengineering*. The manuscript addresses magnitude-dependent nonlinear drift in electrochemical seismometers by proposing an on-board feedforward AI compensation system for real-time embedded deployment.

The central contribution is Wiener-KAN, a compensation framework that combines a Wiener linear layer initialized from measured frequency-response priors with a sign- and symmetry-constrained Kolmogorov-Arnold network nonlinear mapping. The trained KAN spline mappings are precomputed into lookup tables, enabling low-latency on-board inference on an STM32F405 microcontroller. The manuscript also reports a three-dimensional frequency-response dataset capturing amplitude-frequency coupling, an amplitude-frequency loss for frequency-domain drift compensation, and validation under physical response metrics and embedded inference measurements. This combination of sensor nonlinearity characterization, AI compensation, and microcontroller deployment fits the scope of *Microsystems & Nanoengineering*.

The manuscript includes the experimental setup, dataset construction, model architecture, training/evaluation protocol, and embedded deployment workflow, with additional derivations and experimental details provided in the Supplementary Information. The processed dataset and the code used for training, evaluation, embedded export, data partitioning, and metric calculation are publicly available at https://github.com/pikastech/wiener-kan.

We confirm that this manuscript has not been published elsewhere and is not under consideration by another journal. No preprint or related manuscript is currently available or under consideration elsewhere, and there has been no prior discussion with a Springer Nature editor regarding this manuscript. All authors have approved the manuscript and agree with its submission to *Microsystems & Nanoengineering*. We also confirm that no third-party copyrighted material has been reused without authorization. The authors declare no competing interests.

Correspondence concerning this manuscript should be addressed to Hongyuan Yang, State Key Laboratory of Deep Earth Exploration and Imaging, College of Instrumentation and Electrical Engineering, Jilin University, Changchun 130061, China. Email: yang_hy@jlu.edu.cn. Telephone: +86 136 0442 6707.

Thank you for considering our manuscript. We look forward to your response.

Sincerely,

Hongyuan Yang  
On behalf of all authors  
State Key Laboratory of Deep Earth Exploration and Imaging, College of Instrumentation and Electrical Engineering, Jilin University  
Changchun 130061, China  
Email: yang_hy@jlu.edu.cn

## Basis Used for This Draft

- MN Guide for Authors PDF, revised June 12, 2026: requires all authors to have approved submission; requires the manuscript not be under consideration elsewhere; requires author contributions, conflict-of-interest statements, data availability, and relevant permissions/disclosures.
- Springer Nature Support cover-letter checklist: date and target journal; title and article type; background/question; main findings and significance; journal fit; corresponding author and journal-specific ethical requirements; mandatory sentences confirming no other publication/consideration and all-author approval.
- Downloaded Springer Nature cover-letter template: `docs/paper/latex/springer_cover_letter_template_26642004.docx`, which emphasizes novelty/impact/scope, methodological transparency, preprint and publication-ethics disclosures, LLM-use disclosure, and suggested reviewers.
