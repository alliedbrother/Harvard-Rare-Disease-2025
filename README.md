# TrialMatch

## Overview
**TrialMatch** is a platform designed to simplify and accelerate clinical trial recruitment using a swipe-based matching system. Instead of matching individuals for dating, **TrialMatch** connects potential clinical trial participants with organizations conducting medical research. This approach improves user experience, enhances recruitment efficiency, and enables targeted participant selection.

## Features
- **Swipe-Based Matching:** Users and organizations can swipe right (interested) or left (not interested) to streamline trial recruitment.
- **Self-Diagnosis with HPO Mapping:** Users can input symptoms in free text, and the platform maps them to **Human Phenotype Ontology (HPO)** using *Clinphen*.
- **Disease Matching:** The system matches users to relevant clinical trials using *Phrank*, ensuring targeted recruitment.
- **Rare Disease Identification:** Assists niche clinical trials in recruiting participants by identifying rare conditions.
- **Instant Notifications:** When both a user and an organization swipe right, they are notified for further communication.

## Tech Stack
- **Frontend:** React.js (for the swiping interface)
- **Backend:** Node.js with Express.js
- **Database:** MongoDB (for storing user profiles and trials)
- **Machine Learning:** Clinphen & Phrank for HPO mapping and disease matching
- **Hosting:** AWS/GCP/Azure (TBD)
- **Authentication:** OAuth or JWT-based authentication for user security

## How It Works
1. **User Browsing:** Users browse through clinical trials in a card format.
2. **Swipe Interaction:** 
   - Right Swipe → Interested in participating
   - Left Swipe → Not interested
3. **Organization Browsing:** Organizations also swipe on potential participants.
4. **Match Notification:** If both parties swipe right, they receive a notification for further engagement.
5. **Self-Diagnosis Matching:** Users can input symptoms, which are mapped to possible diseases, allowing organizations to find relevant participants proactively.

## Challenges & Future Scope
### Challenges
- Ensuring **data accuracy** from user inputs.
- Compliance with **health regulations (HIPAA, GDPR).**
- Encouraging **user adoption** among clinical trial participants.

### Future Scope
- **AI-powered matching** for enhanced accuracy.
- **Integration with healthcare providers & EHR systems.**
- **Expansion** to more clinical trials and rare disease research.
