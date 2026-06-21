10-Jun-2026


Journal: The Journal of Physical Chemistry Letters
Manuscript ID: jz-2026-00994t.R1
Title: "Selective Vibronic Excitation for Coherent Energy Transport in Photosynthetic and Agrivoltaic Systems"
Author(s): Teguia Kouam, Steve Cabrel; Goumai Vedekoi, Theodore; Tchapet Njafa, Jean-Pierre; Nguenang, Jean-Pierre; Nana Engo, Serge Guy

Dear Dr. Teguia Kouam:

Thank you for submitting your revision for publication in The Journal of Physical Chemistry Letters. It has been examined again by two of the original reviewers, and it appears that a major revision, possibly followed by further reviewer evaluation, will be needed prior to its further consideration for publication. Please see the enclosed reviewers' reports for details regarding the requested changes and/or additions.

When submitting your revised manuscript, you will be able to respond to the comments made by the reviewer(s) by attaching a file containing your detailed responses to all of the points raised by the reviewers.

We allow 30 days for revision, but we encourage you to submit within two weeks. If further delays are necessary, please notify us as soon as possible. Here at JPC Letters we try to expedite the processing of your manuscript, so your prompt response is greatly appreciated.

To Revise Your Manuscript on the Web:

Go to the ACS Publishing Center at https://publish.acs.org to submit your revised manuscript.

Funding Sources: Authors are required to report ALL funding sources and grant/award numbers relevant to this manuscript. Confirm all sources of funding for ALL authors relevant to this manuscript are included in BOTH the submission form and in the manuscript file to meet this requirement. See http://pubs.acs.org/page/4authors/funder_options.html for complete instructions.

ORCID: Authors submitting manuscript revisions are required to provide their own validated ORCID iDs before completing the submission, if an ORCID iD is not already associated with their user profiles. This iD may be provided during original manuscript submission or when submitting the manuscript revision. You can provide only your own ORCID iD, a unique researcher identifier. If your ORCID iD is not already validated and associated with your  user profile, you may do so by following the ORCID-related links in the Email/Name section of your user account. All authors are encouraged to register for and associate their own ORCID iDs with their user profiles. The ORCID iD will be displayed in the published article for any author on a manuscript who has a validated ORCID iD associated with their user account when the manuscript is accepted. Learn more at http://www.orcid.org.

ACS Publications uses Crossref Similarity Check Powered by iThenticate to detect instances of similarity in submitted manuscripts. In publishing only original research, ACS is committed to deterring plagiarism, including self-plagiarism. Your manuscript may be screened for similarity to published material.

Thank you for considering The Journal of Physical Chemistry Letters as a forum for the publication of your work.

With sincere regards,

Prof. Gregory Scholes, Editor-in-Chief
The Journal of Physical Chemistry Letters
Editor Email: eic@jpclett.acs.org

------------------------------------

Reviewer(s)' Comments to Author:

Reviewer: 2

Recommendation: This paper is probably publishable, but major revision is needed; I do not need to see future revisions.

Comments:

The authors have addressed most of the questions raised in my review and have improved the manuscript accordingly. It will help to further revise the manuscript before consideration for publication.

(i)     As stated in the previous review, vibronic resonance and fractional resonance have been analyzed extensively in the context of energy transfer [e.g., JPC. Lett. 6(4), 627 (2015); 13, 6831 (2022)], and the authors should connect to the early work.

(ii)    The authors refer to the concept of ‘polaron transformation’ extensively, but do not seem to actually carry out a polaron transformation or even define a polaron basis.  Perhaps, the authors are referring to the ‘vibronic basis’ (see the above references).  Please clarify.

(iii)   The authors should proofread the manuscript carefully and improve the quality of the presentation.  There are typos and misspellings.



Additional Questions:
Urgency: Moderate

Significance: High

Novelty: High

Scholarly Presentation: Moderate

Is the paper likely to interest a substantial number of physical chemists, not just specialists working in the authors' area of research?: Yes


Reviewer: 3

Recommendation: This paper may be publishable, but major revision is needed; I would like to be invited to review any future revision.

Comments:
The authors have revised their manuscript in many ways. The revisions clarify some but not all of my earlier questions. Important questions remain unanswered, and the revision also raises additional serious issues with this manuscript.

1. The definition for the forward transfer yield is basically 1 minus the survival probability of the initial state. In a multi-state system, the survival probability is not a good measure of a transfer yield. If there is a target state, then the transfer yield should be defined as the long-time (equilibrium) population of that state. If the main consequence of the proposed scheme is to change the survival probability by 20-50%, I don’t see why this is a noteworthy achievement.

2. I still don’t see the spectral density in the paper. Figure 3e shows a strange linear function over the range 600-900 cm-1. I am more willing to believe that the authors used the spectral density shown in the SI, which looks entirely different. In spite of the 12 modes, this spectral density has large gaps between peaks and is more representative of a small molecule than the FMO complex in a protein+solvent medium. However, even more puzzling is the value of the reorganization energy (given only in the SI), which is very small (53 cm-1, including the dissipative term). To my knowledge, bacteriochlorophyll molecules in light harvesting complexes have much larger reorganization energies. The difference may arise from the small number of vibrations included in ref 11: If all vibrational modes were included, the reorganization energy would likely be much larger and comparable to that in other light harvesting complexes.
In addition, the paper mentions 189 modes. FMO has 7 sites, each with 12 modes, so I don’t understand how that number was obtained.

3. The raw simulation results are puzzling and don’t seem to support the claims. Fig. 3b shows the l1 norm, which equals the sum of off-diagonal elements (eq 5). The authors define the coherence lifetime as the 1/e decay time of this quantity. But Fig. 3b does not show a decay. Instead, there are two highly oscillatory curves being compared. Looking at Fig. 3a, which shows populations, I see no decay there either. The population curves are characteristic of isolated systems that lack a dissipative environment. Similar patterns are observed in the inverse participation ratio. The authors write “The primary advantage of preparing these dressed states lies in their decoherence properties”, but I see no decoherence in the figures.

4. Regarding the simulation method, the authors write “PT-HOPS is the theoretical nonperturbative formalism used to handle non-Markovian memory without exponential scaling.” This sentence needs additional clarification, as there are several methods (some with a long history) that avoid exponential scaling. The next sentence mentions size-invariant scaling, O(1) with system size. Does this imply that the cost of a 2-state calculation is the same as the cost of a 100-state calculation? Clearly this is not true. Further, the large computational resources employed in the calculations presented in this paper imply that the method is extremely expensive in comparison to other methods that have been applied to larger systems under more challenging conditions (much larger reorganization energies).
Further, I am still not convinced regarding convergence. The majority of the vibrational modes are at a very low effective temperature at 300 K. How can just 2 Matsubara terms lead to converged results?

5. Much of the discussion used throughout this paper is based on very technical computer jargon that is not suitable for JPCL. For example, sentences such as“This hardware-hardened pipeline was verified through a comprehensive technical audit of three independent refactoring cycles, confirming bit-perfect identical excitonic populations (numerical delta = 0.0) and absolute trace preservation (< 1.0 × 10−12) across all production runs.” or “Hardware-aware scheduling enables converged L = 8 trajectories by autonomously managing the 54GB RAM footprint per path.” are not accessible to a typical JPCL reader. The entire Figure 2 also focuses on a flowchart of the (apparently complex and highly technical) algorithm optimization.


Additional Questions:
Urgency: Low

Significance: Low

Novelty: Moderate

Scholarly Presentation: Moderate

Is the paper likely to interest a substantial number of physical chemists, not just specialists working in the authors' area of research?: Yes

------------------------------------
