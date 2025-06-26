# 🏥 MediCall AI

### An Autonomous Voice Agent That Finds In-Network Providers and Books Your Doctor’s Appointment.

Built in under 24 hours at the Meta LLaMA 4 Hackathon.

---

**[Watch the Demo](https://lnkd.in/gyB8umeX)**

---

## 💡 Why We Built This

Booking a medical appointment should not be this hard. Many of us have experienced the frustration of calling multiple clinics to find an in-network provider who is accepting new patients and doesn't require a referral. Juggling insurance details like PPO vs. HMO, deciphering medical jargon, and dealing with limited office hours can feel like a full-time job.

This is a significant barrier to accessing healthcare for millions. We built MediCall AI to automate this entire process, reducing friction and making healthcare more accessible for everyone. What if we could use the power of modern AI to find the right doctors, call clinics, talk to receptionists, and book appointments for you?

## 🌟 The Impact

MediCall AI is designed to help:

* **Patients overwhelmed by insurance logistics:** No more confusion over what your plan covers.
* **People with phone anxiety or limited availability:** Avoids the stress of making calls and lets you book appointments outside of typical work hours.
* **Non-native English speakers or elderly users:** Bypasses complex phone systems and potential communication barriers.
* **Anyone who wants to skip the hold music:** Save time and avoid the frustration of waiting.

This isn't just a proof-of-concept; it's a step toward a future where healthcare is more accessible and automated for everyone.

## 🧠 How It Works

MediCall AI is an end-to-end autonomous agent that handles the entire appointment booking process.

1.  **User Query:** The user provides a simple request, like: `"I need an otolaryngologist in Seattle, WA."`
2.  **Insurance Parsing:** The user uploads a photo of their insurance card. **LLaMA 4's Multimodal API** analyzes the card to extract the provider, plan type (PPO/HMO), and member ID.
3.  **Provider Search:** Using the insurance details, the system performs a **SERP Google Search API** query to find a list of in-network providers in the specified location.
4.  **Automated Calling:** The agent uses **Twilio** to start calling the clinics from the generated list.
5.  **Live Conversation:** When a human receptionist answers, **LLaMA 4 Maverick** (integrated via **LiveKit**) engages in a live, natural-language conversation to book the appointment.
    * *Note: IVR support is not yet implemented. The agent is designed to speak directly with people.*
6.  **Confirmation:** The agent continues calling down the list until an appointment is successfully booked.
7.  **Summary:** Once booked, the user receives a confirmation with the appointment details.

## 👨‍💻 Built With

* **AI & LLMs:**
    * **Meta LLaMA 4 (Multimodal):** For parsing insurance cards.
    * **Meta LLaMA 4 Maverick:** For live voice conversations.
* **Backend:** FastAPI
* **Frontend:** ReactJS
* **Telephony & Voice:**
    * **Twilio:** For programmatic voice calls.
    * **LiveKit:** For real-time voice streaming with the AI agent.
* **APIs:**
    * **SERP Google Search API:** For finding in-network providers.

## 🚀 The Team

This project was built by an incredible team of developers in under 24 hours:

* Deepansh Saxena
* Dhiren Navani
* Sai Reddy Kumar
* Mohamed Hamzah Weldingwala

## Acknowledgments

* Huge thanks to **Meta** and **Meta for Developers** for providing early access to LLaMA 4.
* Thank you to **Cerebral Valley** for co-hosting an amazing hackathon experience.

Let's make healthcare more accessible, one phone call at a time. 📞🧠

#MetaAI #LLaMA4 #Hackathon #VoiceAI #HealthcareTech #LiveKit #Twilio #MultimodalAI #AI4Good #FastAPI #ReactJS #GenerativeAI #LLMs #Accessibility #TechForGood
