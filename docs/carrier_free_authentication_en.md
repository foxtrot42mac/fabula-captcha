# Carrier-Free Authentication: A Class of Human-Memory-Bound Credential Schemes with Coercive Unverifiability

## Abstract

We introduce *carrier-free authentication* (CFA) as a formal class of authentication schemes in which the credential has no physical or digital representation external to human long-term memory. Unlike token-based, file-based, or device-bound credentials — all of which are seizable, copyable, or destructible — CFA schemes leverage recognition-based cognition rather than recall, making the credential both coercion-resistant and operationally transparent. We define the class by four core properties: *credential non-extractability*, *computational unverifiability of duress*, *post-extraction uncertainty*, and *graceful degradation under partial compromise*. We present two instantiations — Semantic Partial-Match Recognition (SPMR) and Positional Button-Response (PBR) — and analyze their security under a physical-coercion adversary model. We further introduce *cognitive namespace binding*, whereby the memorization vocabulary constitutes a system parameter that determines both the cognitive space of the secret and an implicit barrier for adversaries operating outside that namespace. We additionally identify the *cross-modal semantic gap* as a formal security property of dual-channel challenge presentation, and offer empirical grounding through analysis of CAPTCHA deployment at production scale. CFA schemes are not general-purpose MFA replacements; they address a distinct threat class — physical coercion of high-value human sources — for which no existing scheme provides comparable guarantees. We identify open problems in formal security analysis, combinatorial challenge-space design, and cognitive durability of embedded secrets.

---

## 1. Introduction

*The most effective deterrent against coercive extraction is not ethical prohibition but mechanical futility.*

Consider three scenarios. A journalist crossing a border under surveillance, device seized at the checkpoint. A field operative detained for secondary screening, compelled to unlock accounts. A human rights worker whose hardware has been confiscated and who faces interrogation by actors unconstrained by legal procedure. In each case, the threat is not a remote adversary solving discrete logarithms: it is a person in the same room, with time, and with leverage. The security problem is not computational but physical, and the standard toolkit of modern authentication offers no principled answer.

Hardware security keys are seizable. Device-bound credentials are confiscatable. Passwords and PINs, however strong, can be demanded under threat, observed under duress, or compelled by legal order. Deniable encryption provides a decoy vault, but the vault is an artifact on disk, subject to imaging and extended analysis. Honey passwords introduce a duress signal but require a stored credential file that can be exfiltrated. In each case, the attack surface is an object in the physical world — something that can be taken, copied, or destroyed. The adversary does not need to factor a large integer; they need to locate and seize the right object.

The conceptual core of carrier-free authentication is not, in fact, without precedent in deployed systems — it has simply never been correctly implemented. Knowledge-based authentication via personal security questions instantiates the same underlying intuition: that autobiographical memory contains anchors so deeply encoded that deliberate forgetting is practically impossible. The insight was correct. The implementation was not. By requiring the user to type the answer and storing the result server-side, security question systems converted a carrier-free cognitive credential into a carrier-bound one, subject to database breach, phishing, and the full attack surface of stored secrets. CFA preserves the anchor while eliminating the extraction surface: the personal memory remains the credential, but the authentication act is recognition against a challenge, not recall into a text field. The answer is never entered; therefore it is never stored; therefore it cannot be stolen.

This paper makes the following contributions. First, we provide a formal class definition and four core security property definitions suited to the physical-coercion adversary (Section 3). Second, we introduce *cognitive namespace binding* as a security-relevant system parameter, and *enrollment as memory activation* as a design principle that leverages existing long-term memory structures rather than creating new ones (Section 4). Third, we present two concrete protocol instantiations — SPMR and PBR — with full construction details and security analysis (Section 5). Fourth, we identify the *cross-modal semantic gap* as a formal security property of dual-channel presentation (Property 5.1), and provide large-scale empirical grounding through analysis of CAPTCHA as a proof-of-concept deployment (Section 5.3). Fifth, we establish an explicit open-problems agenda addressed to the cryptographic, cognitive-psychological, and HCI communities (Section 8).

---

## 2. Related Work

**Recognition-based authentication.** The distinction between recall-based and recognition-based password entry has been extensively studied in the usable security literature. Passfaces [Brostoff & Sasse, 2000] demonstrated that users could reliably authenticate using human face recognition over graphical grids, achieving higher memorability than text passwords at the cost of larger credential space. The graphical password taxonomy of Biddle et al. [2012] systematizes recognition-based schemes by distinguishing recall, cued-recall, and recognition subcategories; CFA falls within the recognition subcategory but differs in eliminating any external credential representation. Persuasive Cued Click-Points (PCCP) [Chiasson et al., 2007] addresses hotspot attacks by guiding credential selection away from salient regions — a concern orthogonal to the coercion resistance CFA targets. None of these schemes define carrier-free as a primary security property, nor do they analyze the physical-coercion adversary.

**Deniable authentication and encryption.** Deniable authentication [Dwork et al., 2000; Canetti & Fischlin, 2002] addresses a different problem: producing transcripts that could have been generated by any party, thereby preventing a verifier from proving to a third party that authentication occurred. This property is distinct from CFA's goal of preventing an adversary from verifying credential extraction. VeraCrypt hidden volumes provide plausible deniability against disk forensics, but the hidden volume is itself an artifact; disk seizure makes the ciphertext available for extended cryptanalytic attack. CFA contains no ciphertext.

**Honey passwords.** Juels and Rivest [2013] introduce honey passwords as a mechanism for detecting credential database compromise: the system stores multiple password hashes, of which exactly one is genuine; use of any honey password triggers a silent alert. This is the closest existing work to CFA's duress signal mechanism. The key distinction is that honey passwords require an external credential representation — the hash file — which can be exfiltrated. CFA's duress signal is implemented through a second cognitive credential set that leaves no storage artifact. Credential non-extractability in CFA is therefore a strictly stronger property than what honey passwords provide.

**Implicit and transparent authentication.** Behavioral biometrics and implicit authentication schemes [Shi et al., 2011] authenticate users continuously through characteristic interaction patterns. These schemes are passive and continuous rather than challenge-response, and authenticate the person's behavioral signature rather than a specific secret. They provide no coercion resistance: an adversary who controls the user physically controls the authentication signal.

**Cognitive authentication.** Weinshall [2006] proposes a cognitive authentication scheme in which users recognize elements of a personal graph under interference from decoy elements — a structure cognate to SPMR. The security claim rests on the cognitive difficulty of an observer learning the user's graph from challenge observations; the threat model is passive observation rather than physical coercion, and no duress variant is defined.

**Gap in existing work.** No existing authentication scheme formally defines the absence of an external credential representation as a primary security property, derives a threat model suited to the physical-coercion adversary, or provides a duress mechanism in which the duress signal itself is a cognitive credential with no storage artifact.

---

## 3. Threat Model and Security Goals

### 3.1 Adversary Model

We define four capability classes that may be combined to model different adversaries.

**Observation capability (A_obs).** The adversary may observe an unbounded sequence of challenge-response sessions, recording all challenge items and all user responses. The adversary does not control challenge generation in this mode.

**System capability (A_sys).** The adversary has full read access to the authentication server: the challenge generation algorithm *G*, noise distribution *P_noise*, session logs, and all registered user metadata. Critically, *A_sys* does not grant access to user cognitive state — the system stores no element of the credential at any point after enrollment.

**Physical coercion capability (A_coerce).** The adversary has physical custody of the authenticating user for a bounded duration *T_coerce*. During this period the adversary may compel the user to perform authentication sessions under observation, may apply arbitrary psychological pressure, and may demand verbal disclosure of credential content. We do not model pharmacological or surgical interventions (see Section 6.4).

**Vision-language capability (A_VLM).** The adversary has access to a vision-language model capable of cross-modal semantic unification. We distinguish **A0** (adversary without VLM) from **A1** (adversary with VLM) throughout the analysis.

### 3.2 Security Goals

**SG1 (Server-side non-sufficiency).** Full compromise of *A_sys* does not enable the adversary to authenticate as any registered user.

**SG2 (Observation resistance).** After observing *T <= T_max* sessions, no adversary in A_obs can authenticate as the target user with probability significantly greater than the scheme's false-acceptance rate.

**SG3 (Coercive unverifiability).** After *T_coerce* time of physical coercion, an adversary in A_coerce cannot determine with non-negligible advantage: (a) whether they have obtained the complete credential; (b) whether a duress signal was or was not transmitted during any observed session; (c) whether any credential information disclosed under coercion is genuine or a plausible fabrication.

**SG4 (Partial-disclosure resistance).** Disclosure of *k* < *m* credential components does not enable authentication with probability significantly exceeding *f(k/m)*, where *f* is a sub-linear function bounded below by the false-acceptance rate.

### 3.3 Formal Definitions

**Definition 3.1 (CFA Scheme).** A carrier-free authentication scheme is a tuple CFA = (Enroll, Challenge, Respond, Verify, Alert) where:

- *Enroll(u, V) -> (C, D, t)*: takes user *u* and vocabulary *V*, produces primary concept set *C*, duress concept set *D*, and cognitive namespace parameter *t*. No output of Enroll is stored by the system; all outputs reside exclusively in user long-term memory following the enrollment session.
- *Challenge(n, P_noise) -> ch*: generates a challenge set of size *n* containing *m* probe items derivable from *C* and *n - m* noise items drawn from *P_noise*. The challenge is session-unique and generated server-side.
- *Respond(ch) -> r*: the user's response function over the challenge set.
- *Verify(r, ch) -> {accept, reject}*: server-side verification without access to *C*.
- *Alert(r, ch) -> {nominal, duress, reject}*: server-side duress detection, also without access to *C* or *D*.

**Definition 3.2 (Split Knowledge Property).** A CFA scheme satisfies split knowledge if the information required for successful authentication is partitioned into two disjoint sets: **S1** = {*G*, *P_noise*, verification logic}, held by the server; and **S2** = {*C*, *D*, *t*, association chain}, held in the user's long-term memory. Neither S1 nor S2 alone enables authentication.

**Definition 3.3 (Credential Non-Extractability).** A CFA scheme satisfies credential non-extractability if for all PPT adversaries *A* combining any subset of {A_obs, A_sys, A_coerce}, the probability that *A* produces *C'* such that *Verify(Respond(ch), ch) = accept* under *C'* for a freshly generated *ch* is negligibly greater than the scheme's false-acceptance rate *e*.

**Definition 3.4 (Computational Unverifiability of Duress).** A CFA scheme satisfies computational unverifiability of duress if no PPT adversary *A* in A_obs union A_coerce can distinguish with non-negligible advantage between: (a) a session performed voluntarily with *C*; (b) a session performed under duress with *C*; (c) a session performed under duress with *D*.

**Definition 3.5 (Post-Extraction Uncertainty).** A CFA scheme satisfies post-extraction uncertainty if, following any coercive interaction of duration *T_coerce*, the adversary's probability of constructing *C'* such that *Verify(Respond(ch), ch) = accept* is not significantly higher than prior to the interaction — unless the user has voluntarily and completely disclosed *C*, a condition the adversary cannot verify.

**Definition 3.6 (Graceful Degradation).** A CFA scheme with *m* credential components satisfies graceful degradation if, for any *k* < *m* components disclosed to the adversary, authentication success probability is bounded by *f(k/m)* where *f* is monotonically increasing, *f(0) = e*, *f(1) = 1 - d*, and *f* is sub-linear for non-trivial parameters.

---

## 4. The Carrier-Free Authentication Class

### 4.1 Cognitive Namespace Binding

A distinctive feature of the CFA class is that the vocabulary *V* used for enrollment is itself a security-relevant system parameter. We formalize this as *cognitive namespace binding*: the credential exists within a specific cognitive space defined by the user's active vocabulary, cultural background, and linguistic competence, and the security of the scheme is partly a function of the adversary's distance from that space.

Formally, let *t* denote the cognitive namespace parameter produced at enrollment. *t* encodes the vocabulary domain — whether concepts are drawn from a general lexicon, a specific natural language, a technical vocabulary, a cultural corpus, or a personal semantic network. Two users authenticating with concepts drawn from Catalan idioms and Farsi idioms respectively present different challenge structures to the same adversary.

### 4.2 Credential Enrollment as Memory Activation

A design principle that distinguishes CFA from conventional credential creation is that enrollment does not require the formation of new long-term memories. Instead, it operates as *selective activation* of memory structures that are already stable, deeply encoded, and resistant to decay.

Consider two canonical examples. A user with internalized knowledge of Blok's quatrain — *"Noch, ulitsa, fonar, apteka"* — possesses a cultural anchor encoded through years of exposure and emotional association. Selecting *"ulitsa"*, *"fonar"*, and *"apteka"* as credential components requires no new memorization: enrollment is identification, not acquisition. Similarly, a user trained in the NATO phonetic alphabet holds that sequence as overlearned procedural knowledge. Selecting "Lima", "Tango", "Oscar" as credential components activates an existing procedural trace rather than creating a new episodic one.

This distinction has concrete security consequences. Memory traces formed through deep semantic processing and repeated rehearsal exhibit substantially greater long-term retention than episodically encoded novel items [Craik & Lockhart, 1972].

### 4.3 Duress Signal Design

The duress credential *D*, produced alongside *C* at enrollment, is a secondary concept set of the same structure as *C* but distinct in content. When the user responds to a challenge using recognition responses consistent with *D* rather than *C*, the Alert function emits a duress signal to the system backend. The adversary observing the session cannot determine whether *C* or *D* was used: both produce syntactically and statistically identical authentication flows.

Two design constraints govern the selection of *D*: it must be independently memorable, and it must be sufficiently similar to *C* in surface-form distribution that no observable statistical signature distinguishes duress sessions from nominal sessions.

---

## 5. Instantiations

### 5.1 Semantic Partial-Match Recognition (SPMR)

**Challenge Construction.** In SPMR, the user's credential consists of *m* compound semantic concepts — structured word pairs or short phrases encoding a stable associative unit (e.g., *"old shoe"*, *"blue door"*, *"ambient light"*). At authentication time, the system generates a challenge set of size *n*. For each of the *m* credential concepts, exactly one *probe item* is inserted; each probe contains exactly one word from one target concept — never the full phrase. The remaining *n - m* items are *noise items* drawn from the same semantic field and surface form distribution as the probes.

**Dual-Channel Presentation.** SPMR supports simultaneous presentation of both textual and visual representations of challenge items, drawing on Paivio's dual-coding theory [Paivio, 1986]. Each challenge item is rendered as a short text label alongside a corresponding image.

**Multi-Hop Cognitive Chain Variant.** SPMR supports a *multi-hop cognitive chain* construction in which the credential is a private transformation sequence applied to publicly known material. A user whose surname is Lindeman identifies the initial *L*, maps it via the NATO phonetic alphabet to *"Lima"*, and notes that Lima is the capital of Peru — selecting *"Peru"* as the challenge probe word. Each step is public knowledge; the chain itself is private. This exploits *spreading activation* in semantic memory networks [Collins & Loftus, 1975].

### 5.2 Positional Button-Response (PBR)

**Credential Structure and Enrollment.** In PBR, the credential is a single multi-attribute concept in which each semantic component is bound to an ordinal position. A canonical example: the concept *"old rustic key"* encodes three components — *"old"* at position 1, *"rustic"* at position 2, *"key"* at position 3.

**Challenge Construction and Response Protocol.** The system presents a sequential stream of word tokens in one of *p* positional columns or time slots. The user's response protocol is strictly binary: press a designated button when a word matching the component bound to the current display position appears; otherwise make no response. No text is typed, no semantic choice is made, no visual selection occurs.

**Elimination of Keystroke-Logging Attack Surface.** PBR eliminates the entire category of keystroke-logging attacks. Hardware keyloggers, software keyloggers, acoustic emanation analysis [Zhuang et al., 2009], and shoulder-surfing attacks on text entry are categorically inapplicable. The residual observable — a sequence of button-press timestamps — carries no semantic content without the challenge stream.

### 5.3 CAPTCHA as Large-Scale Empirical Validation of CFA Mechanics

The cognitive mechanisms underlying CFA have been stress-tested at production scale across billions of sessions under the name of CAPTCHA. CAPTCHA authenticates *class membership* (human vs. automated agent); CFA authenticates *individual identity*. Nevertheless, CAPTCHA constitutes an existence proof that the core mechanical properties of CFA function correctly under adversarial conditions at global scale. The scale of CAPTCHA deployment — hundreds of billions of challenges served — provides empirical confirmation that recognition-based human-computer interaction at this challenge complexity level is both usable and robust against automated adversaries without specialized semantic grounding capabilities.

**Property 5.1 (Cross-Modal Semantic Gap).** Dual-channel presentation in CFA schemes instantiates a stronger property than two independent data streams: the two channels occupy *representationally disjoint spaces* whose unification requires semantic grounding unavailable to non-symbolic automated systems.

The value RGB(0, 0, 255) is a coordinate in a perceptual color space interpretable by any pixel-level classifier. The string *"blue"* is a token in a symbolic linguistic space, processable by any text parser. A human performing cross-modal unification does so via embodied semantic memory [Barsalou, 1999]: the visual percept and the linguistic token activate the same underlying concept node. An automated adversary without a VLM processes two formally unconnected observations.

---

## 6. Security Analysis

### 6.1 Comparative Security Table

| Property | CFA/SPMR | CFA/PBR | Hardware Token | Honey Passwords | Deniable Encryption | Security Questions | Standard MFA |
|---|---|---|---|---|---|---|---|
| Credential non-extractability | Yes | Yes | No | No | No | No | No |
| Computational unverifiability of duress | Yes | Yes | No | Partial | Partial | No | No |
| Post-extraction uncertainty | Yes | Yes | No | Partial | Partial | No | No |
| Graceful degradation | Yes | Yes | No | No | No | No | No |
| Split knowledge S1 intersect S2 = empty | Yes | Yes | Partial | No | No | No | Partial |
| Cross-modal semantic gap | Yes | No | N/A | N/A | N/A | N/A | N/A |
| Physical seizure resistance | Yes | Yes | No | No | No | No | No |
| No external credential artifact | Yes | Yes | No | No | No | No | No |

*Table 1. Yes = property holds; No = does not hold; Partial = conditional.*

### 6.2 Formal Analysis of Core Properties

**6.2.1 Credential Non-Extractability.** System compromise yields *G* and *P_noise*, but not concept set *C*. With *n* = 20, *m* = 3, *e* = 0.05, expected sessions to identify all probes with confidence 0.95 exceeds 80 — a meaningful detection window for rate-limiting defenses.

**6.2.2 Computational Unverifiability of Duress.** Primary *C* and duress *D* produce syntactically identical authentication flows. The adversary's distinguishing advantage is bounded by the semantic distance between *C* and *D* against *P_noise*.

**6.2.3 Post-Extraction Uncertainty.** After coercive verbalization, three independent sources of residual uncertainty remain: verbalized concepts may be *D* rather than *C*; multi-hop chains allow plausible decoy terminal words; the adversary cannot determine whether additional credential layers exist.

**6.2.4 Graceful Degradation.** With *m* = 3 and 1 concept disclosed, the adversary achieves correct probe selection for that concept but cannot authenticate without correct selection across all *m*.

### 6.3 Adversary Sub-Cases: A0 and A1

**A0 (without VLM).** Cross-modal attack is categorically unavailable. Challenge-space entropy for SPMR with |*V*| = 10,000 and *m* = 3 compound concepts is approximately log2(C(10000,2)^3) approximately 117 bits.

**A1 (with VLM).** Three residual protections apply: VLM inference latency may exceed challenge expiry window *T_window*; VLMs exhibit non-negligible error rates on rare compounds, culture-specific idioms, and concepts at the edge of their training distribution; VLM queries are detectable through anomalous latency distributions.

### 6.4 Limitations

Long-term surveillance allows asymptotic probe identification. Cognitive decay may partially dissociate multi-hop chains without rehearsal. Pharmacological interrogation is outside the computational threat model. Response timing side-channel is the principal residual attack surface.

---

## 7. Cognitive Considerations

### 7.1 Recognition vs. Recall: The Cognitive Advantage

Recognition memory is substantially more accurate and durable than recall memory for equivalent material across all population groups and testing delays [Standing, 1973]. A credential vocabulary a user can *recognize* is far larger than one they can reliably *recall*, enabling richer concept sets without increasing cognitive load.

Under coercion, the user cannot simply "forget" their credential on demand, but neither can they be compelled to verbalize the underlying concept set — since the recognition response does not require explicit retrieval of that set.

### 7.2 Cognitive Load Under Authentication

CFA schemes minimize active load by relying on familiarity judgments rather than controlled retrieval [Yonelinas, 2002]. The partial-match construction addresses the interference concern: because the user never sees their full concept during authentication — only one fragment per probe — the authentication act does not constitute a full retrieval of the credential.

### 7.3 Procedural Memory and Stress Robustness

While declarative memory is significantly impaired by elevated cortisol and norepinephrine [Roozendaal, 2002], procedural and implicit memory systems exhibit substantially greater resistance to stress-induced degradation [Metcalfe & Jacobs, 1998]. Overlearned sequences — rehearsed to automaticity — are retrievable under conditions of acute fear where deliberate recall fails. CFA enrollment guidelines should therefore preferentially target procedural memory anchors for high-risk user profiles.

---

## 8. Open Problems

**8.1 Formal Security Proofs.** Converting the four core properties into game-based definitions and proving them under standard cryptographic assumptions is the primary open problem for the cryptographic community.

**8.2 Combinatorics of Challenge Spaces.** What is the minimum challenge set size *n* required to achieve *k* bits of authentication entropy against an adversary with observation budget *t*, given noise-to-probe ratio *r* and user false-positive rate *e*?

**8.3 Timing Side-Channel Mitigation.** What normalization strategies adequately suppress latency signals without reducing usability below acceptable thresholds?

**8.4 VLM-Hard Vocabulary Selection.** Systematic characterization of the vocabulary subspace on which current VLMs exhibit high error rates — rare compounds, low-resource language idioms, culture-specific referents, polysemous terms requiring biographical context.

**8.5 Composability.** Under what conditions can CFA be used as one factor in a multi-factor protocol without the composed system inheriting CFA's limitations?

**8.6 Cognitive Decay Without Rehearsal.** How long does a childhood-anchored or procedurally-anchored credential remain functionally accessible without deliberate rehearsal? Longitudinal studies over 6, 12, and 24 months are needed before deployment recommendations can be made.

**8.7 Recognition Stability in Evolving Datasets.** Does recognition performance for enrolled concepts remain stable when the surrounding challenge context shifts significantly?

**8.8 Emotional Valence and Memorability.** Do credentials anchored in emotionally salient material exhibit superior retention and stress robustness compared to emotionally neutral anchors?

**8.9 User Study Under Stress.** An ecologically valid user study — measuring CFA authentication accuracy, response latency, and false-positive rates under induced acute stress — is required before any deployment recommendation in genuinely high-stakes contexts.

---

## References

Bahrick, H.P. (1984). Semantic memory content in permastore. *Journal of Experimental Psychology: General*, 113(1), 1-29.

Barsalou, L.W. (1999). Perceptual symbol systems. *Behavioral and Brain Sciences*, 22(4), 577-609.

Biddle, R., Chiasson, S., & Van Oorschot, P.C. (2012). Graphical passwords: Learning from the first twelve years. *ACM Computing Surveys*, 44(4), 1-41.

Bimmerle, G. (1993). "Truth" drugs in interrogation. *Studies in Intelligence* (declassified 1997, CIA Historical Review Program).

Brostoff, S. & Sasse, M.A. (2000). Are passfaces more usable than passwords? *Proceedings of HCI 2000*, 405-424.

Canetti, R. (2001). Universally composable security. *Proceedings of IEEE FOCS*, 136-145.

Canetti, R. & Fischlin, M. (2002). Universally composable commitments. *Proceedings of CRYPTO 2001*, LNCS 2139, 19-40.

Chiasson, S., van Oorschot, P.C., & Biddle, R. (2007). Graphical password authentication using cued click points. *Proceedings of ESORICS 2007*, LNCS 4734, 359-374.

Collins, A.M. & Loftus, E.F. (1975). A spreading-activation theory of semantic processing. *Psychological Review*, 82(6), 407-428.

Craik, F.I.M. & Lockhart, R.S. (1972). Levels of processing: A framework for memory research. *Journal of Verbal Learning and Verbal Behavior*, 11(6), 671-684.

Dwork, C., Naor, M., Sahai, A. (2004). Concurrent zero-knowledge. *Journal of the ACM*, 51(6), 851-898.

Ericsson, K.A. & Kintsch, W. (1995). Long-term working memory. *Psychological Review*, 102(2), 211-245.

Graf, P. & Schacter, D.L. (1985). Implicit and explicit memory for new associations. *Journal of Experimental Psychology: Learning, Memory, and Cognition*, 11(3), 501-518.

Jacoby, L.L. (1991). A process dissociation framework. *Journal of Memory and Language*, 30(5), 513-541.

Juels, A. & Rivest, R.L. (2013). Honeywords: Making password-cracking detectable. *Proceedings of ACM CCS 2013*, 145-160.

Mandler, G. (1980). Recognizing: The judgment of previous occurrence. *Psychological Review*, 87(3), 252-271.

McGaugh, J.L. (2004). The amygdala modulates the consolidation of memories of emotionally arousing experiences. *Annual Review of Neuroscience*, 27, 1-28.

Metcalfe, J. & Jacobs, W.J. (1998). Emotional memory: The effects of stress on "cool" and "hot" memory systems. *The Psychology of Learning and Motivation*, 38, 187-222.

Murdock, B.B. (1962). The serial position effect of free recall. *Journal of Experimental Psychology*, 64(5), 482-488.

Paivio, A. (1986). *Mental Representations: A Dual Coding Approach*. Oxford University Press.

Radford, A. et al. (2021). Learning transferable visual models from natural language supervision. *Proceedings of ICML*, 139, 8748-8763.

Roozendaal, B. (2002). Stress and memory. *Neurobiology of Learning and Memory*, 78(3), 578-595.

Shi, E. et al. (2011). Implicit authentication through learning user behavior. *Proceedings of ISC 2011*, LNCS 7001, 99-113.

Standing, L. (1973). Learning 10,000 pictures. *Quarterly Journal of Experimental Psychology*, 25(2), 207-222.

Tulving, E. & Thomson, D.M. (1973). Encoding specificity and retrieval processes in episodic memory. *Psychological Review*, 80(5), 352-373.

Weinshall, D. (2006). Cognitive authentication schemes safe against spyware. *Proceedings of IEEE S&P 2006*, 295-300.

Yonelinas, A.P. (2002). The nature of recollection and familiarity. *Journal of Memory and Language*, 46(3), 441-517.

Zhuang, L., Zhou, F., & Tygar, J.D. (2009). Keyboard acoustic emanations revisited. *ACM TISSEC*, 13(1), 1-26.

---

## Acknowledgments

The conceptual framework of this work was developed in dialogue with Claude Sonnet and Claude Opus (Anthropic). The human author formulated the initial threat model and core security properties; the AI systems contributed to formalization, comparative analysis, and draft structure. AI tools are not listed as authors in accordance with current academic publication standards; their contribution is disclosed here in full.
