# 🚀 [Tips Hindawi](https://www.tipshindawi.com/) Internship (August–October) 2026

> 🎓 This project was built during the [ **Tips Hindawi** ](https://www.tipshindawi.com/) **Internship (August–October) 2026**.

## 👤 Participant

| Field            | Value                                |
| ---------------- | ------------------------------------ |
| Full Name        | Abdelrhman Moubarak                  |
| Project Name     |Edge Case Finder                      |
| GitHub Username  |Abdelrhman-Moubarak                   |
| Internship Batch | August–October 2026                  |
| Training Program | Large Language Models (LLMs) Program |
| Organization     | [**Edrak for Ai**](https://edrak4ai.com/en)                         |

---

# 📖 Project Overview

Edge Case Finder generates edge-case tests for a Python function. You paste the function and a plain-English description of what it should do, and the app returns a set of tricky inputs with their expected outcomes.

The expected outcomes come from the description, not from the code. This matters because a test whose expected value is copied from a buggy function will pass and hide the bug. Here, a reference function is written from the description alone and used to compute the expected values.

---

# 📂 File Structure

```text

edge-case-finder/
├── app.py                  # Streamlit UI
├── requirements.txt
├── README.md
├── llm_server.ipynb        # Model server, run on Kaggle
├── models/
│   ├── edge_case.py        # EdgeCase, EdgeCaseSuite
│   └── prompts.py          # generator, reviewer and reference function prompts
└── src/
    ├── llm_client.py       # LangChain wrapper around the remote Qwen endpoint
    ├── chains.py           # generation pipeline
    └── runner.py           # runs the reference function in a subprocess

```

---

# ✨ Features

* Two-stage generation: one model call proposes candidate cases, a second reviews them and removes duplicates and weak cases
* Expected values are computed by running a reference function written only from the description
* Cases that cannot be verified are shown separately as dropped cases instead of crashing the run
* Live progress status while generating
* Download the results as Markdown or JSON

---

# 🛠️ Technologies Used

* Python
* Streamlit
* LangChain
* Pydantic
* Qwen3-8B, served from a Kaggle notebook through ngrok
* FastAPI (model server)

---

# ⚙️ Installation

Requires Python 3.10 or newer.

```powershell
git clone https://github.com/Abdelrhman-Moubarak/edge-case-finder.git
cd edge-case-finder
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Create a `.env` file next to `app.py`:

```text
NGROK_URL=<your ngrok public url>
API_KEY=<your server api key>
```

The model server must be running before you start the app. It is a Kaggle notebook that loads Qwen3-8B and exposes a `/generate` endpoint through ngrok. Copy the public URL it prints into `NGROK_URL`.

---

# 🚀 Usage

```powershell
streamlit run app.py
```

1. Paste your function in the left box.
2. Describe what it should do in the right box. Include limits, rules and what should be rejected.
3. Click **Generate edge cases**.
4. Read the cases, then download them as Markdown or JSON if you want.

A run takes several minutes with the current model, so keep the tab open until it finishes.

---

# 📸 Demo

Add screenshots, GIFs, or a demo video.

---

# 📈 Results

On a shipping-cost function with a documented set of rules, one run kept 8 cases and dropped 0, in about 6.5 minutes. The cases covered the weight boundaries, zero and negative inputs, and the express option, and the expected values matched a hand check against the description.

---

# 🔮 Future Improvements

* **Run the cases against the real function:** add a tester that runs each generated call on the user's code and compares the result with the expected value, so bugs like a wrong rate or a wrong boundary are reported as failing tests.
* **Generate more cases on demand:** a "Generate more" button that asks the model for new cases different from the ones already produced, removes duplicate calls, and reuses the saved reference function so only the new cases need expected values.
* **Faster model serving:** replace the 8-bit model with a 4-bit or fp16 setup.

---

# 📚 About the Internship

This project was developed as part of the [**Tips Hindawi**](https://www.tipshindawi.com/) **Internship (August–October) 2026**, and it will be showcased on the official [Tips Hindawi](https://www.tipshindawi.com/) website.

[Tips Hindawi](https://www.tipshindawi.com/) is the internships department of [**Edrak for Ai**](https://edrak4ai.com/en), and the internship encourages participants to build real-world projects, apply practical skills, and showcase their work through GitHub.

For more information about the internship, training programs, and upcoming batches, visit the official [Tips Hindawi](https://www.tipshindawi.com/) website.

---

# 📄 License

This project is shared for educational and portfolio purposes.