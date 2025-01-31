import streamlit as st
import textwrap
import fitz  # PyMuPDF
import io
import google.generativeai as genai
from docx import Document
from IPython.display import Markdown

def to_markdown(text):
    text = text.replace('•', '  *')
    return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

# List of 5 API keys
api_keys = [
    st.secrets["api_keys"]["key1"],
    st.secrets["api_keys"]["key2"],
    st.secrets["api_keys"]["key3"],
    st.secrets["api_keys"]["key4"],
    st.secrets["api_keys"]["key5"],
]

# Track the last used API key index
api_key_index = 0

# Function to set API key and configure the model in order
def configure_api_key():
    global api_key_index
    while api_key_index < len(api_keys):
        try:
            key = api_keys[api_key_index]  # Select the current API key
            genai.configure(api_key=key)
            model = genai.GenerativeModel('gemini-pro')  # Configure the model with the API key
            api_key_index += 1  # Move to the next key for the next time
            return model
        except Exception as e:
            st.error(f"Failed to configure API with key {key}: {e}")
            api_key_index += 1  # Move to the next API key
    # If all keys fail, show a message and return None
    st.error("Sorry, the service is temporarily unavailable. Please try again later.")
    return None  # If all keys fail

# Initialize the model using the first working API key
model = configure_api_key()

# Function to extract text from PDF file using fitz
def extract_text_from_pdf(uploaded_file):
    text = ''
    pdf_bytes = io.BytesIO(uploaded_file.read())
    with fitz.open(stream=pdf_bytes, filetype="pdf") as pdf_file:
        for page_num in range(pdf_file.page_count):
            page = pdf_file[page_num]
            text += page.get_text()
    return text

# Function to extract text from DOCX file using python-docx
def extract_text_from_docx(uploaded_file):
    text = ''
    doc = Document(io.BytesIO(uploaded_file.read()))
    for para in doc.paragraphs:
        text += para.text + '\n'
    return text

def main():
    st.title('🔍 Outil Analyse des CVs Gratuit')

    # Create a navigation sidebar
    page = st.sidebar.radio("📑 Sélectionner une Page", ("Analyser vos CV", "Lettre de Motivation Personalisé", "À propos de nous"))
    if page == "À propos de nous":

        st.markdown("""
        ### 📊 Analysez vos CVs gratuitement avec IFCAR Job
        Chez **IFCAR Job**, nous savons combien il est crucial de mettre en valeur votre parcours professionnel.  
        C’est pourquoi nous avons conçu un **outil gratuit d’analyse de CV**, à la fois **simple**, **rapide**, et **précis**.

        ### 🚀 Pourquoi utiliser notre outil ?
        - **Recommandations personnalisées** : Optimisez la présentation de votre CV.  
        - **Analyse des mots-clés** : Alignez votre candidature avec les attentes des recruteurs.  
        - **Suggestions sur les compétences** : Adaptez votre CV au secteur visé.

        ### 🎯 Pourquoi choisir IFCAR Job ?
        Avec plus de **12 ans d’expertise dans le recrutement**, nous aidons candidats et recruteurs à se connecter efficacement.  
        Notre outil d’analyse de CV reflète notre engagement à offrir des solutions modernes et performantes pour réussir dans le monde de l’emploi.

        📌 **Essayez notre analyse de CV dès aujourd’hui** et boostez vos chances de décrocher votre prochain poste !
        """)

    else:
        # File uploader with unique key
        uploaded_file = st.file_uploader('Uploader votre PDF ou WORD CV 📤', type=['pdf', 'docx'], key='file_uploader_1')




        if uploaded_file is not None:
            file_extension = uploaded_file.name.split('.')[-1].lower()

            # Extract text based on file type (PDF or DOCX)
            if file_extension == 'pdf':
                text = extract_text_from_pdf(uploaded_file)
            elif file_extension == 'docx':
                text = extract_text_from_docx(uploaded_file)
            else:
                text = ''

            if text:
                if page == "Analyser vos CV":
                    job = st.text_input('Post Préféré 💼:', placeholder="Optionnel")
                    languages = st.selectbox('Langue prefere 🌍:', ['Français', 'English', 'Espagnol'])
                    execute_button = st.button("Executer l'Analysis 🔥")

                    if execute_button:
                        try:
                            executed = False
                            # If job is empty, only show top jobs and tips, not compatibility
                            if job == '':
                                prompt1 = f"The text you've been provided is a Resume (the Resume could be in the language {languages}). You are an HR supervisor specialized in Recruitment and Resume checking. I want from you to check based on the text of the resume the Top 5 best suitable jobs for the candidate resume with bullet points on why in {languages}"
                                prompt5 = f"The text you've been provided is a Resume (the Resume could be in FR or ENG). You are an HR supervisor specialized in Recruitment and Resume checking. I want from you based on the text of the resume to give 5 tips and tricks to improve the resume in all terms in {languages}"

                                combined_text1 = prompt1 + "\n" + text
                                response1 = model.generate_content(combined_text1)

                                combined_text5 = prompt5 + "\n" + text
                                response5 = model.generate_content(combined_text5)

                                st.write(response1.text)  # Display the top 5 jobs response
                                st.write('----------------------------------------------------------------------------------------------------')
                                st.write(response5.text)  # Display the resume improvement tips
                                st.markdown('<p style="color:red;">Ajoutez votre travail préféré pour plus d\'analyse</p>', unsafe_allow_html=True)  # Encourage adding job for further analysis

                            else:
                                # If job is provided, display compatibility with the job
                                prompt1 = f"The text you've been provided is a Resume (the Resume could be in the language {languages}). You are an HR supervisor specialized in Recruitment and Resume checking. I want from you to check based on the text of the resume the Top 5 best suitable jobs for the candidate resume with bullet points on why in {languages}"
                                prompt4 = f"The text you've been provided is a Resume (the Resume could be in the language {languages}). You are an HR supervisor specialized in Recruitment and Resume checking. I want from you to check based on the text how much is compatible with the job: {job} in percentage and give the reason and some tips in {languages}"
                                prompt5 = f"The text you've been provided is a Resume (the Resume could be in FR or ENG). You are an HR supervisor specialized in Recruitment and Resume checking. I want from you based on the text of the resume to give 5 tips and tricks to improve the resume in all terms in {languages}"

                                combined_text1 = prompt1 + "\n" + text
                                response1 = model.generate_content(combined_text1)

                                combined_text4 = prompt4 + "\n" + text
                                response4 = model.generate_content(combined_text4)

                                combined_text5 = prompt5 + "\n" + text
                                response5 = model.generate_content(combined_text5)

                                # Display responses for top jobs, job compatibility, and resume tips
                                st.write(response1.text)  # Display the top 5 jobs response
                                st.write('----------------------------------------------------------------------------------------------------')
                                st.write(response4.text)  # Display job compatibility response
                                st.write('----------------------------------------------------------------------------------------------------')
                                st.write(response5.text)  # Display the resume improvement tips

                            executed = True

                            button_placeholder = st.empty()

                            if executed:  # Ensure results are shown before displaying the button
                                with button_placeholder:
                                    st.markdown('[🔍 Trouvez Votre Job sur IFCAR Job 🚀](https://ifcarjob.com)', unsafe_allow_html=True)

                        except Exception as e:
                            st.error(f"Erreur dans l'analyse de votre CV: {e}")

                    else:
                        st.info("Cliquez sur 'Executer' pour démarrer l'analyse.")

                elif page == "Lettre de Motivation Personalisé":
                    # Logic for "Lettre de Motivation" page
                    with st.form(key='letter_form'):
                        job = st.text_input('Post Préféré 💼:', placeholder="Optionnel")
                        company_name = st.text_input('Nom de l\'entreprise 🏢:', placeholder="Optionnel")
                        job_description = st.text_area('Description du Poste 📋:', placeholder="Optionnel")
                        languages = st.selectbox('Langue Préféré 🌍:', ['Français', 'English', 'Espagnol'])
                        execute_button = st.form_submit_button("Générer la Lettre de Motivation 📝")

                    if execute_button:
                        try:
                            # Ensure job is not empty
                            if not job:
                                st.error("Le post préféré est requis pour générer la lettre de motivation.")
                            else:
                                # Modify the prompt with job, company, and job description
                                prompt2 = f"The text you've been provided is a Resume (the Resume could be in the language {languages}). You are an HR supervisor specialized in Recruitment and Resume checking. I want you to generate a personalized cover letter based on the resume. If job and company are provided, incorporate them into the letter: The job is '{job}' at {company_name}, and the job description is as follows: '{job_description}'. If not, base the letter on the resume information alone. The letter should be in {languages}."

                                combined_text2 = prompt2 + "\n" + text
                                response2 = model.generate_content(combined_text2)

                                st.write(response2.text)

                        except Exception as e:
                            st.error(f"Erreur lors de la génération de la lettre de motivation: {e}")

            else:
                st.warning("Votre CV n'est pas compatible. Changer votre 📄")
        else:
            st.info("")
        
st.image("Logo.png", caption="Ifcar Solutions", use_container_width=True)

if __name__ == '__main__':
    main()

st.markdown('[🔍 Trouvez Votre Job sur IFCAR Job 🚀](https://ifcarjob.com)', unsafe_allow_html=True)

