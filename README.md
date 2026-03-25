# Robotics Project Page Generator
**Automated Academic Website Builder**

This tool allows you to instantly generate high-fidelity academic project pages from your research papers. It is designed for lab projects and rapid dissemination, ensuring your work has a professional home online even before it hits ArXiv.

---

### 🚀 Key Features
* **Full-Text Intelligence**: Upload a PDF or provide an ArXiv link; the app uses GPT-4o to extract technical details and write comprehensive Methodology and Results sections.
* **High-Fidelity Design**: Generates a single-file `index.html` using Tailwind CSS, featuring a clean, responsive layout inspired by the DGPPO project page.
* **Live Preview**: View your website interactively inside the app before you download it.
* **Contextual Placeholders**: Includes smart SVG icons and captions for figures and videos based on your paper's actual content.

---

### 🛠 How to Use
1. **Choose Input Mode**:
    * **Fetch from ArXiv**: Paste the link to your paper.
    * **Upload PDF**: Drag and drop your local `.pdf` file.
    * **Manual Entry**: For drafts that aren't finalized yet.
2. **Generate**: Click the "Generate Website" button. The system will process your paper text (approx. 15–20 seconds).
3. **Live Preview**: Review the generated site in the preview pane to ensure content accuracy.
4. **Download**: Click **⬇️ Download index.html** to save your finished page.
5. **Final Polish**: Open the HTML file and replace the `` tags with your actual images and videos.

---

### 💻 Local Development
To run this application locally:

1. **Clone the repo**:
   ```bash
   git clone [https://github.com/akilasarva/paper-to-website.git](https://github.com/akilasarva/paper-to-website.git)
   cd paper-to-website

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt

3. **Set your API Key**:
   Create a `.streamlit/secrets.toml` file and add your key:
   ```toml
   OPENAI_API_KEY = "sk-proj-your-key-here"

4. **Run the app**:
   ```bash
   streamlit run app.py

### 🌐 Hosting
This app is designed to be hosted on **Streamlit Community Cloud**. 

1. **GitHub**: Push your `app.py`, `requirements.txt`, and `README.md` to a GitHub repository.
2. **Streamlit Share**: Connect your repository to [share.streamlit.io](https://share.streamlit.io/).
3. **Secrets**: In the Streamlit deployment dashboard, go to **Settings > Secrets** and paste your API key:
   ```toml
   OPENAI_API_KEY = "sk-proj-your-actual-key-here"

4. **Deploy**: Once saved, your app will be live at a custom URL for your lab to use.
