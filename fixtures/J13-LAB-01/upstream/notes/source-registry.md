# Source Registry

This registry identifies the source records referenced by the current study notes. It does not contain the complete source corpora.

## Verification rule

A study may quote the owner-approved wording while its record remains `source_verification: pending`. The record cannot become training-approved until the exact source artifact, revision, quotation, rights state, and locator have been verified.

## Current sources

| Handle prefix | Source | Role | Rights posture | Verification state |
|---|---|---|---|---|
| `SP01-SRC-001` | SBL Greek New Testament | Greek text and exact source span | CC BY 4.0, attribution required | Pending exact source acquisition and lock |
| `SP01-SRC-002` | MorphGNT, SBLGNT edition | Lemma and morphology | Source-plan-approved component, exact revision still to be locked | Pending exact source acquisition and lock |
| `SP01-SRC-003` | American Standard Version, 1901 | Historical English translation | Public domain | Pending exact digital-edition verification |
| `SP01-SRC-004` | World English Bible Classic | Modern English translation | Public domain, trademark integrity applies | Pending exact digital-edition verification |
| `SP01-SRC-005` | Abbott-Smith Greek Lexicon TEI | Bounded lexical evidence | Public-domain source component, exact artifact still to be locked | Pending exact source acquisition and lock |

## Current John 1:5 locators

```text
SP01-SRC-001#John.1.5
SP01-SRC-002#John.1.5:κατέλαβεν
SP01-SRC-003#John.1.5
SP01-SRC-004#John.1.5
SP01-SRC-005#καταλαμβάνω
```

## Usage boundaries

- Exact biblical wording must remain tied to a named translation and edition.
- The Greek text, morphology, and lexical evidence remain separate source layers.
- A lexicon's possible senses are not all automatically active in one verse.
- Different English wording does not by itself establish a different Greek manuscript reading.
- Public-domain or openly licensed status does not automatically authorize training. Training requires a separate owner decision.

## Additional open comparison sources for John 3

| Handle prefix | Source | Role | Rights posture | Verification state |
|---|---|---|---|---|
| `EDITORIAL-SRC-KJV-001` | King James Version, exact eBible digital edition pending | Public-domain comparison rendering “born again” in John 3:3 and 3:7 | Public domain in the United States. Editorial comparison only until exact edition and jurisdictional release handling are reviewed. | Pending exact digital-edition verification and later formal source admission |
| `EDITORIAL-SRC-YLT-001` | Young's Literal Translation, exact eBible digital edition pending | Public-domain comparison rendering “born from above” in John 3:3 and 3:7 | Public domain. Editorial comparison only until exact edition is verified and formally admitted. | Pending exact digital-edition verification and later formal source admission |

## Current John 3 locators

```text
SP01-SRC-001#John.3.2-12
SP01-SRC-001#John.3.31
SP01-SRC-001#John.19.11
SP01-SRC-001#John.19.23
SP01-SRC-002#John.3.3:γεννηθῇ
SP01-SRC-002#John.3.3:ἄνωθεν
SP01-SRC-002#John.3.4:δεύτερον
SP01-SRC-002#John.3.7:σοι
SP01-SRC-002#John.3.7:ὑμᾶς
SP01-SRC-002#John.3.8:πνεῦμα
SP01-SRC-003#John.3.3-12
SP01-SRC-003#Ezekiel.36.25-27
SP01-SRC-004#John.3.3-12
SP01-SRC-004#John.3.3.note
SP01-SRC-004#John.3.8.note
EDITORIAL-SRC-KJV-001#John.3.3-7
EDITORIAL-SRC-YLT-001#John.3.3-7
```

## John 3 verification boundary

The SBLGNT, MorphGNT, ASV, and WEB source identities are already registered, but `SOURCE-PLAN-01` activated only the John 1:5 vertical slice. The John 3 locators above therefore remain editorial references pending a later exact source-verification record.

The KJV and YLT are public-domain comparison candidates, but they aren't admitted to the durable corpus, retrieval index, or training data merely by appearing in this editorial record.

The John 3 study may remain owner-approved and publication-draft while verification is pending. It can't become training-approved until:

- the exact SBLGNT and MorphGNT John 3 and John 19 artifacts and locators are locked;
- the exact ASV, WEB, KJV, and YLT digital-edition identities and quotations are verified;
- the WEB translator notes are captured from the exact admitted edition;
- the John 3 and John 19 occurrences of **ἄνωθεν** are reproduced from the locked Greek corpus;
- the Ezekiel 36 background is preserved as a plausible intertext rather than settled proof of one interpretation;
- the owner separately approves a training-safe projection.

## Additional open comparison sources for John 4

| Handle prefix | Source | Role | Rights posture | Verification state |
|---|---|---|---|---|
| `EDITORIAL-SRC-OEB-001` | Open English Bible, U.S. spelling, exact release record pending | Public-domain comparison rendering of John 4:10–14, including “a spring welling up within him, a source of eternal life” | CC0/public domain. Editorial comparison only until the exact release and digital artifact are locked and formally admitted. | Pending exact digital-edition verification and later formal source admission |
| `EDITORIAL-SRC-BBE-001` | Bible in Basic English, exact eBible digital edition pending | Public-domain comparison rendering of John 4:10–14, including “a fountain of eternal life” | Public domain in the United States as represented by eBible. Editorial comparison only until the exact digital artifact is locked and formally admitted. | Pending exact digital-edition verification and later formal source admission |

## Current John 4 locators

```text
SP01-SRC-001#John.3.1-12
SP01-SRC-001#John.4.10-14
SP01-SRC-001#John.7.37-39
SP01-SRC-001#Acts.3.8
SP01-SRC-001#Acts.14.10
SP01-SRC-002#John.4.14:πηγὴ
SP01-SRC-002#John.4.14:ὕδατος
SP01-SRC-002#John.4.14:ἁλλομένου
SP01-SRC-002#John.4.14:εἰς
SP01-SRC-005#ἅλλομαι
SP01-SRC-004#John.4.10-14
EDITORIAL-SRC-OEB-001#John.4.10-14
EDITORIAL-SRC-BBE-001#John.4.10-14
```

## John 4 verification boundary

The SBLGNT, MorphGNT, WEB, and Abbott-Smith source identities are already registered, but `SOURCE-PLAN-01` activated only the John 1:5 vertical slice. The John 4, John 7, and Acts locators above therefore remain editorial references pending a later exact source-verification record.

The OEB and BBE are open or public-domain comparison candidates, but they aren't admitted to the durable corpus, retrieval index, or training data merely by appearing in this editorial record.

The John 4 study may remain published while verification is pending. It can't become training-approved until:

- the exact SBLGNT and MorphGNT John 4, John 7, Acts 3, and Acts 14 artifacts and locators are locked;
- the exact WEB, OEB, and BBE digital-edition identities and quotations are verified;
- the Abbott-Smith entry for **ἅλλομαι** is locked and reviewed;
- the morphology and agreement of **ἁλλομένου** with **ὕδατος** are reproduced from the locked Greek corpus;
- the other New Testament uses of **ἅλλομαι** are reproduced from the locked Greek corpus;
- the John 7 connection is preserved as a discourse-level Johannine link rather than a claim that every detail of John 4 is directly defined by John 7;
- the owner separately approves a training-safe projection.

## Current John 14–15 locators

```text
SP01-SRC-001#John.14.1
SP01-SRC-001#John.14.2
SP01-SRC-001#John.14.4-11
SP01-SRC-001#John.14.23
SP01-SRC-001#John.15.1-6
SP01-SRC-002#John.14.1:πιστεύετε
SP01-SRC-002#John.14.2:μοναί
SP01-SRC-002#John.14.6:ὁδός
SP01-SRC-002#John.14.6:ἀλήθεια
SP01-SRC-002#John.14.6:ζωή
SP01-SRC-002#John.14.6:οὐδείς
SP01-SRC-002#John.14.6:διά
SP01-SRC-002#John.14.23:μονήν
SP01-SRC-002#John.15.2:αἴρει
SP01-SRC-002#John.15.2:καθαίρει
SP01-SRC-002#John.15.3:καθαροί
SP01-SRC-002#John.15.4:μείνατε
SP01-SRC-004#John.14.6
SP01-SRC-004#Genesis.28.10-22
SP01-SRC-004#Exodus.25.8
SP01-SRC-004#Ezekiel.37.26-28
SP01-SRC-004#Psalm.27
SP01-SRC-004#Matthew.16.24-25
SP01-SRC-004#Ephesians.2.18-22
SP01-SRC-004#Hebrews.10.19-23
SP01-SRC-004#1Thessalonians.4.16-17
SP01-SRC-004#Revelation.21.1-4
EDITORIAL-SRC-KJV-001#John.14.6
EDITORIAL-SRC-NIV-001#John.15.1-4
```

## John 14–15 verification boundary

The SBLGNT, MorphGNT, WEB, KJV, and NIV source identities are used here for editorial study, but `SOURCE-PLAN-01` activated only the John 1:5 vertical slice. These John 14 and John 15 locators remain editorial references pending a later exact source-verification record.

The John 14–15 reflection may remain published while verification is pending. It can't become training-approved until:

- the exact SBLGNT and MorphGNT John 14 and John 15 artifacts and locators are locked;
- the exact WEB and KJV John 14:6 wording and digital-edition identities are verified;
- the NIV John 15:1–4 edition, locator, attribution, wording, and quotation permission are verified;
- the relationship between **μονή** and **μένω** is checked against an admitted lexicon;
- the forms and contextual ranges of **αἴρει**, **καθαίρει**, **καθαροί**, and **μείνατε** are reproduced from the locked Greek corpus;
- the John 15:6 context is preserved when evaluating whether **αἴρει** is best represented as removing or lifting;
- the broader Old and New Testament connections remain identified as thematic unless a direct textual dependence is separately established;
- the owner separately approves a training-safe projection that excludes restricted NIV wording.

## Editorial-only sources for John 15

| Handle prefix | Source | Role | Rights posture | Verification state |
|---|---|---|---|---|
| `EDITORIAL-SRC-NIV-001` | New International Version, exact edition record pending | Owner-supplied bounded quotations from John 15:1–5 for public reflections | Copyrighted editorial use only. No full-text corpus, retrieval index, redistribution, or training use is authorized. | Pending exact edition, locator, wording, and quotation-permission verification |
| `EDITORIAL-SRC-NIRV-001` | New International Reader's Version, exact edition record pending | Phrase-level comparison behind “remain joined” | Copyrighted editorial use only. No full-text corpus, retrieval index, redistribution, or training use is authorized. | Pending exact edition, locator, wording, and quotation-permission verification |
| `EDITORIAL-SRC-CONCORDANCE-001` | Greek concordance for Strong's 3306, μένω | Preliminary New Testament and Johannine frequency counts | Secondary editorial reference only. It isn't an authoritative Greek corpus and isn't training-approved. | Pending independent count against an exact locked Greek corpus |

## Current John 15 locators

```text
SP01-SRC-001#John.1.38-39
SP01-SRC-001#John.15.4-10
SP01-SRC-002#John.15.4:μείνατε
SP01-SRC-003#John.15.4-5
SP01-SRC-004#John.15.4-5
EDITORIAL-SRC-NIV-001#John.15.4-5
EDITORIAL-SRC-NIRV-001#John.15.4
EDITORIAL-SRC-CONCORDANCE-001#G3306
```

## John 15 verification boundary

The SBLGNT and MorphGNT source identities are already registered, but `SOURCE-PLAN-01` activated only the John 1:5 vertical slice. The John 15 locators above therefore remain editorial references pending a later exact source-verification record.

The John 15 reflection may remain owner-approved and publication-draft while verification is pending. It can't become training-approved until:

- the exact SBLGNT and MorphGNT John 15 artifacts and locators are locked;
- the NIV and NIrV edition identities and quotation permissions are verified;
- the New Testament frequency counts are independently reproduced from the locked Greek corpus;
- the owner separately approves a training-safe projection that excludes restricted translation wording.

## Current John 13 locators

```text
SP01-SRC-001#John.10.17-18
SP01-SRC-001#John.13.1-38
SP01-SRC-001#John.15.3
SP01-SRC-002#John.13.1:εἰς_τέλος
SP01-SRC-002#John.13.2:γινομένου
SP01-SRC-002#John.13.4:ἱμάτια
SP01-SRC-002#John.13.6:σύ
SP01-SRC-002#John.13.8:οὐ_μὴ_νίψῃς
SP01-SRC-002#John.13.8:μέρος
SP01-SRC-002#John.13.10:λελουμένος
SP01-SRC-002#John.13.10:νίψασθαι
SP01-SRC-002#John.13.10:καθαροί
SP01-SRC-002#John.13.13:διδάσκαλος
SP01-SRC-002#John.13.14:ὀφείλετε
SP01-SRC-002#John.13.15:ὑπόδειγμα
SP01-SRC-002#John.13.16:δοῦλος
SP01-SRC-002#John.13.16:ἀπόστολος
SP01-SRC-002#John.13.17:μακάριοι
SP01-SRC-002#John.13.18:πτέρναν
SP01-SRC-002#John.13.19:ἐγώ_εἰμι
SP01-SRC-002#John.13.23:κόλπῳ
SP01-SRC-002#John.13.25:στῆθος
SP01-SRC-002#John.13.26:ψωμίον
SP01-SRC-002#John.13.30:νύξ
SP01-SRC-002#John.13.31:ἐδοξάσθη
SP01-SRC-002#John.13.34:ἐντολὴν_καινήν
SP01-SRC-003#John.13.1-38
SP01-SRC-004#John.13.1-38
SP01-SRC-004#Psalm.41.9
EDITORIAL-SRC-KJV-001#John.13.1-38
```

## John 13 verification boundary

The SBLGNT, MorphGNT, ASV, WEB, and KJV source identities are used here for editorial study, but `SOURCE-PLAN-01` activated only the John 1:5 vertical slice. The John 10, John 13, John 15, and Psalm 41 locators above remain editorial references pending a later exact source-verification record.

The John 13 study may remain owner-approved without a public-post plan while verification is pending. It can't become training-approved until:

- the exact SBLGNT and MorphGNT John 10, John 13, and John 15 artifacts and locators are locked;
- the exact ASV, WEB, and KJV John 13 digital editions and quotations are verified;
- the Greek forms and contextual ranges of **εἰς τέλος**, **μέρος**, **λελουμένος**, **νίψασθαι**, **ὑπόδειγμα**, **δοῦλος**, **ἀπόστολος**, **μακάριοι**, **ἐγώ εἰμι**, **ψωμίον**, **ἐδοξάσθη**, and **ἐντολὴν καινήν** are reproduced from the locked Greek corpus and reviewed;
- the John 13:2, 13:10, and 13:32 textual variants are verified against an admitted critical apparatus rather than inferred only from English translations or editorial notes;
- the possible echo between laying aside and taking up garments in John 13 and laying down and taking up life in John 10 remains marked as a literary possibility rather than a lexical identity;
- the inference that Judas received the footwashing remains distinguished from an explicit narrative statement;
- “it was night” remains identified as literal narrative time with possible Johannine symbolic resonance rather than a symbolism claim established by the noun alone;
- the relationship among washing, bathing, baptism, initial cleansing, continuing cleansing, and participation in Jesus remains open where the passage doesn't settle a complete theological system;
- the owner separately approves a training-safe projection.
