Dear Dr. Teguia Kouam:

Thank you for submitting your manuscript for publication in The Journal of Physical Chemistry Letters. It has been examined by expert reviewers who have concluded that the work is of potential interest to the readership of The Journal of Physical Chemistry Letters; however, it appears that a major revision, possibly followed by further reviewer evaluation, will be needed prior to its further consideration for publication. Please see the enclosed reviewers' reports for details regarding the requested changes and/or additions.

When submitting your revised manuscript, you will be able to respond to the comments made by the reviewer(s) by attaching a file containing your detailed responses to all of the points raised by the reviewers.

We allow 30 days for revision, but we encourage you to submit within two weeks. If further delays are necessary, please notify us as soon as possible. Here at JPC Letters we try to expedite the processing of your manuscript, so your prompt response is greatly appreciated.

Please note that you may receive a follow-up message within 24 hours describing the non-scientific changes you must also make to your manuscript, in accordance with our author guidelines, before you submit the revision. It is important to address these changes in your revision so that processing your manuscript can proceed without further delay. Please include a point-by-point response in the Cover Letter for your revision detailing how each formatting item was addressed.

To Revise Your Manuscript on the Web:

Go to the ACS Publishing Center at https://publish.acs.org to submit your revised manuscript.

Format: Your revised manuscript must adhere to The Journal of Physical Chemistry Letters format.  An author checklist is available at http://pubs.acs.org/paragonplus/submission/jpchax/jpclcd_checklist.pdf and The Journal of Physical Chemistry Letters author guidelines are available at https://pubs.acs.org/page/jpclcd/submission/authors.html.

Supporting Information: If the manuscript is accompanied by any supporting information for publication, a brief description of the supplementary material is required in the manuscript. The appropriate format is: Supporting Information. Brief statement in nonsentence format listing the contents of the material supplied as Supporting Information.

Funding Sources: Authors are required to report ALL funding sources and grant/award numbers relevant to this manuscript. Confirm all sources of funding for ALL authors relevant to this manuscript are included in BOTH the submission form and in the manuscript file to meet this requirement. See http://pubs.acs.org/page/4authors/funder_options.html for complete instructions.

ORCID: Authors submitting manuscript revisions are required to provide their own validated ORCID iDs before completing the submission, if an ORCID iD is not already associated with their user profiles. This iD may be provided during original manuscript submission or when submitting the manuscript revision. You can provide only your own ORCID iD, a unique researcher identifier. If your ORCID iD is not already validated and associated with your  user profile, you may do so by following the ORCID-related links in the Email/Name section of your user account. All authors are encouraged to register for and associate their own ORCID iDs with their user profiles. The ORCID iD will be displayed in the published article for any author on a manuscript who has a validated ORCID iD associated with their user account when the manuscript is accepted. Learn more at http://www.orcid.org.

We also require a graphic for the "Table of Contents" with all submissions. We ask that you include a graphic immediately after the Abstract under the header “TOC Graphic.” Instructions are available at https://pubs.acs.org/page/jpclcd/submission/authors.html .

ACS Publications uses Crossref Similarity Check Powered by iThenticate to detect instances of similarity in submitted manuscripts. In publishing only original research, ACS is committed to deterring plagiarism, including self-plagiarism. Your manuscript may be screened for similarity to published material.

Thank you for considering The Journal of Physical Chemistry Letters as a forum for the publication of your work.

With sincere regards,

Prof. Gregory Scholes, Editor-in-Chief
The Journal of Physical Chemistry Letters
Editor Email: eic@jpclett.acs.org

------------------------------------

Reviewer(s)' Comments to Author:

Reviewer: 1

Recommendation: This paper is not recommended because the material is not appropriate for The Journal of Physical Chemistry Letters.

Comments:

This paper claims that spectral filtering of the excitation pulse ("spectral bath engineering") extends excitonic coherence lifetimes by 20–50% and improves forward transfer yields by 25% in the FMO complex at room temperature. While the computational effort is substantial and the topic is timely, the manuscript suffers from a fundamental conceptual misframing, internal numerical inconsistencies, and insufficiently justified theoretical arguments. In my assessment, the manuscript is not suitable for publication in its current form and requires major revisions addressing the following issues.

1. The authors claim to employ the Process Tensor Hierarchy of Pure States (PT-HOPS), yet the acknowledgment and data availability sections explicitly reference the MesoHOPS library. These are not identical methods. Could the authors provide a more detailed and self-contained account of the precise algorithm used, clarifying how their implementation relates to the standard PT-HOPS and MesoHOPS formalisms? This distinction is important for readers to assess the accuracy and applicability of the reported results.

2. The paper's defining claim—"spectral bath engineering"—is fundamentally misleading. The observed differences in dynamics are the trivially expected consequence of preparing different initial states. This must be clearly distinguished from genuine bath engineering (e.g., cavity QED modifications of the vacuum density of states), which would actually alter spectral density or the electromagnetic mode structure.

3. Figure 1 is insufficiently detailed. The main results figure (Fig. 1) lacks essential information for the reader to independently assess the data. Specifically, the axis labels and tick marks for panels (a)–(d) are either missing or illegible—the x-axis numbering and units cannot be discerned. Could the authors replot Figure 1 with clearly labeled and numbered axes, legible fonts, and explicit units on all panels?

4. Figure 2(a): physically unmotivated temperature profile. The x-axis of Figure 2(a) is labeled "Time (days)" and spans 0 to 350, apparently representing a seasonal temperature cycle. This presentation is puzzling and physically irrelevant to the ultrafast dynamics under study.

5. The paper contains directly contradictory specifications for key numerical parameters. The main text states that the hierarchy is truncated at L=10 with K=4 Matsubara terms (page 4), whereas SI Table S1 lists L=6, K=6. Furthermore, SI Test 1 reports 0.9% deviation between L=8 and L=10, while Table S4 lists the hierarchy depth deviation as 1.2%. Which parameters were actually used? This inconsistency fundamentally undermines confidence in the reported numerical results.

Additional Questions:
Urgency: Moderate

Significance: Moderate

Novelty: Moderate

Scholarly Presentation: Low

Is the paper likely to interest a substantial number of physical chemists, not just specialists working in the authors' area of research?: No

-----

Reviewer: 2

Recommendation: This paper may be publishable, but major revision is needed; I would like to be invited to review any future revision.

Comments:

The authors present a numerical calculation of energy transfer dynamics in FMO to demonstrate the possibility of quantum control in light-harvesting systems to enhance quantum coherence. The topic is interesting and relevant, but parts of the scientific presentation are sketchy: Discussions on FMO systems, vibronic effects, noise-enhanced energy transfer, are somewhat limited (see comments below). The numerical method is not a focus and can be moved to Appendix. The cited references are rather incomplete. An illustration of the FMO model and proposed control scheme will help. Further, it would be insightful to design a simple solvable model to explain the results. In short, the authors shall revise the manuscript considerably before it can be further considered.

1. The term of ‘bath-engineering’ is misleading. The bath here refers to photons, or more precisely, laser pulses, which are treated classically, not as quantized photons. So, a proper description of the study will be ‘quantum control of light-harvesting energy transfer via initial excitation’.

2. Vibronic coherence in light-harvesting energy transfer has been explored extensively by Graham Fleming [J. Phys. Chem. Lett. 6(4), 627 (2015)], Greg Scholes [Annual review of physical chemistry 66 (1), 69-96 (2015)], and other leading scientists. In these studies, vibronic resonance is identified as a possible mechanism for efficient energy transfer and is particularly relevant for long-range vibronic-assisted transfer.

3. FMO has been extensively modelled in literature. Is the spectral density used in Eq. (3) based on a realistic modelling of FMO? Several groups including David Coker and Ulrich Kleinekathöfer have carried out detailed numerical modelling of FMO and have updated the spectral density.

4. The authors refer to environment-assisted quantum transport (ENAQT) extensively. The mechanism leads to maximal energy transfer efficiency in FMO at optimal temperature, reorganization energy, and spatial-temporal correlation. [New J. Phys. 12, 105012 (2010) and subsequent studies] In the context of the current study, can the vibronic coupling or laser excitation be optimized?

5. Laser control via selective mode excitation is an interesting idea. In its natural state, FMO serves as a linker between the base-plate and reaction center in the green bacteria and is not directly exposed to sunlight. Thus, the proposed coherent excitation may be relevant in laser control experiments but not in the biological setting.

Additional Questions:
Urgency: Moderate

Significance: High

Novelty: High

Scholarly Presentation: Moderate

Is the paper likely to interest a substantial number of physical chemists, not just specialists working in the authors' area of research?: Yes


Reviewer: 3

Recommendation: This paper may be publishable, but major revision is needed; I would like to be invited to review any future revision.

Comments:
This manuscript poses an intriguing question, regarding the possible manipulation of coherence loss through tailored light pulses. Although it is clear that turning off certain components of the spectral density should decrease or delay decoherence, the particular avenues for achieving such an outcome are less obvious. While the manuscript gives many details in the SI, it omits important information regarding key features of the suggested process and the results are not presented clearly. For example, the manuscript mentions a laser pulse being applied, but the functional form of the time-dependent field amplitude and its timing relative to photoexcitation are not given. Further, I cannot identify the coherence enhancement (reported as a modest percentage extension of various quantities such as the inverse participation ratio) in Figure 1, where each panel shows a single noisy line (not a comparison) without time units, thus making it impossible to appreciate the gains attained through pulse application.

Most importantly however, the model spectral density employed in the manuscript, which has four peaks, is not representative of the true spectral density of bacteriochlorophyll molecules, which consists of many modes with frequencies spread over the entire range, and the additional low-frequency component required to model the solvent/protein medium. Further, the Huang-Rhys factors used in the calculations are quite small and correspond to very small reorganization energies. These choices may have been dictated by limitations of the method employed for this investigation. Regardless, it is hard to imagine that the results are representative of energy transfer in photosynthetic light harvesting.

Last, it is unclear to me whether the simulation results are exact, as claimed. The method employed involves many adjustable/truncation parameters. The comparison against HEOM for a smaller system does not resolve the accuracy question because some similar truncation assumptions are made there.


Additional Questions:
Urgency: Moderate

Significance: Moderate

Novelty: Moderate

Scholarly Presentation: High

Is the paper likely to interest a substantial number of physical chemists, not just specialists working in the authors' area of research?: Yes


---------
### Supplementary Journal Cover Invitation

To improve and transform your experience of publishing with ACS journals, we are currently developing the ACS Publishing Center. As a result, you may experience interactions and communications from different systems for some elements of the process during this transition. We aim to continue providing you with the best service and appreciate your patience as we work through these changes.

28-Apr-2026

Manuscript ID: jz-2026-00994t
Manuscript Type: Letter
Title: "Quantum-coherent spectral engineering: non-Markovian dynamics in photosynthetic energy transfer under engineered photon baths"
Author(s): Teguia Kouam, Steve Cabrel; Goumai Vedekoi, Theodore; Tchapet Njafa, Jean-Pierre; Nguenang, Jean-Pierre; Nana Engo, Serge Guy


Dear Dr. Teguia Kouam:

Did you know that we offer a great way to promote your work with a journal cover? When you submit your revised manuscript, you can also submit cover art to be considered for one of The Journal of Physical Chemistry Letters’ upcoming front or supplementary covers. Covers are featured on The Journal of Physical Chemistry Letters website and the related article page. For more information about the benefits of having your cover selected and answers to some common questions, please visit http://pubs.acs.org/page/4authors/promotion/journal-cover-image.html or contact our Publications Support team at support@services.acs.org.

If selected, ACS Publications will provide instructions for sharing for your work with our network via social media and a high-resolution file for use in scientific talks, displays, or wherever you see fit. You will be notified after acceptance of your manuscript if your cover art is selected for publication.

If you are interested in participating, you must submit the proposed cover image and a short caption at the same time as your revised manuscript. For more information about cover art at The Journal of Physical Chemistry Letters, including dimensions and other guidance, please review the Author Guidelines at https://pubs.acs.org/page/jpclcd/submission/authors.html.

All authors have the opportunity to submit Cover Art with a revision, and therefore submission of a cover does not guarantee selection. Your cover image will be evaluated among the submissions we receive. You are responsible for obtaining and providing any needed permissions if you (or another author) did not create any portion of the image.

Up to four supplementary covers are selected per issue, increasing the chance of your art being featured. While images chosen for the front cover will be published at no cost to the author, there is a fee to contribute to production costs if your art is selected for a supplementary cover. Full details about program pricing, including the discount available to ACS Members at the Premium package level, can be found at http://pubs.acs.org/page/4authors/promotion/journal-cover-image.html.

All art submitted for consideration for a supplementary cover will also be considered for a front cover. However, if you want to be considered only for the front cover, and not a supplementary cover, please respond accordingly to the Journal Covers question.

ACS Publications is proud to support you throughout the publication of your research, and we are delighted that you have chosen us as your partner.

With best wishes,

ACS Publications
American Chemical Society


------

### Manuscript Formatting Request - Non-scientific changes

To improve and transform your experience of publishing with ACS journals, we are currently developing the ACS Publishing Center. As a result, you may experience interactions and communications from different systems for some elements of the process during this transition. We aim to continue providing you with the best service and appreciate your patience as we work through these changes.

28-Apr-2026

Manuscript ID: jz-2026-00994t
Manuscript Type: Letter
Title: "Quantum-coherent spectral engineering: non-Markovian dynamics in photosynthetic energy transfer under engineered photon baths"
Author(s): Teguia Kouam, Steve Cabrel; Goumai Vedekoi, Theodore; Tchapet Njafa, Jean-Pierre; Nguenang, Jean-Pierre; Nana Engo, Serge Guy

Dear Dr. Teguia Kouam:

You recently received a Revision Request from Dr. Gregory Scholes.  In addition to addressing the Editor's concerns and the requests of the reviewers, we request your assistance with the following issues so that we may process your manuscript as quickly as possible:

1.      Please remove the section headings from your manuscript file, e.g., Introduction, Results and Discussion, Conclusion. Experimental section headings as well as paragraph headings are okay.

2.      Include a TOC graphic illustrating the significance of the paper. For TOC guidelines and size requirements, please see the following link: https://pubsapp.acs.org/paragonplus/submission/toc_abstract_graphics_guidelines.pdf? Please label the TOC graphic as “TOC Graphic”. A caption describing the TOC graphic is not needed and will not be used.

3.      Please make sure that your Supporting Information file does not include any highlighting or tracked changes and colored text.

For more details, please see the Author Guidelines, which can be found here: https://pubs.acs.org/page/jpclcd/submission/authors.html

We look forward to receiving your revised manuscript.

Be sure that the final versions of your manuscript file and any Supporting Information files intended for publication (including the pdf versions, if provided) are free of all markup elements, such as track changes, comments, colored text, highlights, and sticky notes.

If desired, you may annotate a copy of the manuscript to show revisions and track changes for the benefit of the reviewers.   This marked manuscript should be uploaded electronically in the File Upload section as "Supporting Information for Review Only" during submission of your revision.

Thank you for considering The Journal of Physical Chemistry Letters as a forum for the publication of your work.

Sincerely,

Jelena Krivokapic
The Journal of Physical Chemistry Letters
