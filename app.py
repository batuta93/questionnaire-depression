import logging
import streamlit as st
import random
import time
import pandas as pd
import io
import json
from datetime import datetime
from fpdf import FPDF
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Tuple, Dict, Any

# Configuration du logging
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

# --- Initialisation de la session ---
if 'page' not in st.session_state:
    st.session_state.page = "page_bienvenue"
if 'yiri_questionnaire' not in st.session_state:
    st.session_state.yiri_questionnaire = None
if 'results_displayed' not in st.session_state:
    st.session_state.results_displayed = False
if 'error_message' not in st.session_state:
    st.session_state.error_message = ""
if 'rerun_key' not in st.session_state:
    st.session_state.rerun_key = 0
if 'test_results' not in st.session_state:
    st.session_state.test_results = {}
if 'historical_results' not in st.session_state:
    st.session_state.historical_results = []
if 'current_question_index' not in st.session_state:
   st.session_state.current_question_index = 0
if 'pause_requested' not in st.session_state:
    st.session_state.pause_requested = False
if 'anonymous_mode' not in st.session_state:
   st.session_state.anonymous_mode = False


# --- CSS custom ---
st.markdown(
    """
    <style>
        body {
            font-family: 'Arial', sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
        }
        .stApp {
            max-width: 800px;
            margin: 0 auto;
            padding: 20px;
        }
         @media (max-width: 768px) {
            .stApp {
                padding: 10px; /* Réduire le padding sur les petits écrans */
            }
        }
        h1, h2, h3, h4, h5, h6 {
            color: #007bff;
            text-align: center;
        }
          @media (max-width: 768px) {
            h1 {
              font-size: 2em; /* Réduire la taille du titre sur les petits écrans */
            }
        }

        .stButton > button {
            background-color: #007bff;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 5px;
            cursor: pointer;
             margin: 5px;

        }
         @media (max-width: 768px) {
              .stButton > button {
                    padding: 8px 16px;
                    font-size: 0.9em;
              }
         }

        .stButton > button:hover {
            background-color: #0056b3;
        }
        .stRadio > div > div > div:nth-child(1) label{
            font-size: 18px;
            color: grey;

        }
        @media (max-width: 768px) {
              .stRadio > div > div > div:nth-child(1) label {
                  font-size : 16px;
              }
         }
        .stCheckbox > label {
            font-size : 16px
        }
         @media (max-width: 768px) {
             .stCheckbox > label {
                    font-size : 14px
              }
         }
         .stTextInput > div > div > input {
            border: 2px solid #ddd;
            border-radius : 5px
        }
        .stTextInput > div > div > input:focus{
            outline: none;
            border: 2px solid #007bff;
        }


        .report-container {
            background-color: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
        }


    </style>
    """,
    unsafe_allow_html=True
)
# --- Fonctions utilitaires ---
def centered_text(text, level="h2"):
    """Affiche un texte centré."""
    st.markdown(f"<div style='text-align:center;'><{level}>{text}</{level}></div>", unsafe_allow_html=True)

def centered_button(label, key=None, disabled=False):
    """Affiche un bouton centré."""
    col = st.columns(3)[1]  # Utilisez la colonne du milieu pour centrer le bouton
    with col:
        return st.button(label, key=key, disabled=disabled)

def centered_checkbox(label, key=None):
    """Affiche un checkbox centré."""
    col = st.columns(3)[1]
    with col:
        return st.checkbox(label, key=key)

def centered_radio(label, options, key=None, index=None):
    """Affiche un radio centré."""
    col = st.columns(3)[1]
    with col:
        return st.radio(label, options, key=key, index=index)


def centered_text_input(label, placeholder, key=None):
     """Affiche une entrée de texte centrée."""
     col = st.columns(3)[1]
     with col :
         return st.text_input(label, placeholder=placeholder, key=key)

def centered_markdown(text):
    """Affiche un markdown centré."""
    st.markdown(f"<div style='text-align:center;'>{text}</div>", unsafe_allow_html=True)

# --- Fonctions pour chaque page ---
def page_bienvenue():
    with st.container():
        centered_text("Bienvenue dans l'application Yiri", "h1")
        centered_markdown("Cette application a été conçue pour vous aider à évaluer votre état émotionnel. Veuillez répondre aux questions avec honnêteté. Vos réponses seront utilisées de manière anonyme et confidentielle.")
        centered_markdown("Pour commencer le questionnaire, cliquez sur le bouton ci-dessous.")
        st.session_state.anonymous_mode = centered_checkbox("Utiliser le mode anonyme", key="checkbox_anonyme")
        if centered_button("Commencer"):
            st.session_state.page = "page_conditions"

def page_conditions():
    with st.container():
        centered_text("Conditions d'acceptation", "h1")
        centered_markdown("Avant de commencer le questionnaire, veuillez lire et accepter les termes et conditions.")
        centered_markdown("**Conditions d'utilisation :**")
        centered_markdown("1. Vous devez être âgé de plus de 18 ans pour utiliser ce questionnaire.")
        centered_markdown("2. Les réponses sont confidentielles et ne seront utilisées qu'à des fins d'analyse.")
        centered_markdown("3. Vous devez répondre de manière honnête aux questions.")

        terms_accepted = centered_checkbox("J'accepte les termes et conditions", key="terms_accepted")

        if terms_accepted:
            if centered_button("Continuer"):
                st.session_state.page = "page_accueil"

def page_accueil():
   with st.container():
      centered_text("Bienvenue sur Yiri", "h1")
      centered_markdown("Vous pouvez maintenant commencer le questionnaire.")

      # Bouton pour commencer le questionnaire
      if centered_button("Commencer le questionnaire"):
         st.session_state.yiri_questionnaire = YiriQuestionnaire()
         st.session_state.page = "page_questionnaire"

def page_questionnaire():
    with st.container():
        centered_text("Questionnaire de Dépression Yiri", "h1")

        if st.session_state.yiri_questionnaire is None:
            st.error("Erreur : Le questionnaire n'a pas été initialisé.")
            return

        # Afficher la barre de progression
        progress_bar = st.progress(0)
        st.session_state.yiri_questionnaire.ask_questions(progress_bar)

        if st.session_state.yiri_questionnaire.is_completed():
            st.session_state.page = "page_resultats"

def page_resultats():
    with st.container():
        centered_text("Résultats du Questionnaire", "h1")

        if st.session_state.results_displayed:
            st.info("Les résultats ont déjà été affichés.")
            return

        if st.session_state.yiri_questionnaire and st.session_state.yiri_questionnaire.is_completed():
          try:
              result, recommendation, total_score = st.session_state.yiri_questionnaire.analyze_responses()
              with st.container():
                st.markdown("<div class='report-container'>", unsafe_allow_html=True)
                st.write(f"**Résultats :** {result}")
                st.write(f"**Recommandations :** {recommendation}")
                st.write(f"**Score Total :** {total_score}")
                st.markdown("</div>", unsafe_allow_html=True)
              if not st.session_state.anonymous_mode:
                st.session_state.yiri_questionnaire.save_results_to_csv()
              else :
                  st.write("**Vous utilisez le mode anonyme, vos résultats ne sont pas sauvegardés.**")
              
              with st.container():
                # Stocker l'historique des résultats
                if 'historical_results' not in st.session_state:
                   st.session_state.historical_results = []
                st.session_state.historical_results.append(
                   {"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Score": total_score, "Result":result, "Recommandation": recommendation}
                )
                st.session_state.results_displayed = True

                # Téléchargement PDF
                pdf_file = create_pdf_report(result, recommendation, total_score, st.session_state.historical_results[-1])
                st.download_button(label="Télécharger le rapport PDF", data=pdf_file, file_name="report.pdf", mime="application/pdf")

                # Partage par Email
                if not st.session_state.anonymous_mode:
                   email = centered_text_input("Partager par e-mail (Attention, vos données personnelles seront utilisées)", placeholder="exemple@email.com", key="email_input")
                   if centered_button("Envoyer par Email", key="send_email_button"):
                        if email:
                           send_email(email, result, recommendation, total_score, st.session_state.historical_results[-1])
                           st.success("Email envoyé!")
                        else:
                           st.warning("Veuillez entrer une adresse email valide.")
                else:
                    st.write("L'envoi par email n'est pas disponible en mode anonyme.")

              with st.container():
                  # Afficher les fonctionnalités d'aide
                  st.subheader("Outils d'auto-assistance")
                  with st.expander("Techniques de relaxation"):
                    st.write("Ici, tu trouveras des exercices de respiration, de pleine conscience, ou des visualisations guidées.")
                  with st.expander("Journaling"):
                    st.write("Utilise cette section pour tenir un journal de tes pensées et émotions.")
                    journal_text = st.text_area("Votre Journal", height=150)
                    if st.button("Enregistrer le Journal"):
                        st.session_state.journal_text = journal_text
                        st.success("Journal enregistré")
                        st.write(f"Contenu du journal : {journal_text}")
                  with st.expander("Planification d'activités"):
                     st.write("Utilise cette section pour organiser tes activités.")
                     st.text_input("Ajouter une activité", key="activity_input")
                     if st.button("Ajouter l'activité"):
                        st.write("Activité Ajoutée")
                  with st.expander("Suivi de l'humeur"):
                       st.write("Permet de suivre l'évolution de ton humeur au fil du temps.")

              with st.container():
                  st.subheader("Ressources Utiles")
                  with st.expander("Annuaire de professionnels"):
                      st.write("Ici, tu trouveras un annuaire de psychologues, psychiatres ou autres professionnels.")
                  with st.expander("Lignes d'écoute"):
                      st.write("Ici, tu trouveras les lignes d'écoute disponibles.")
                  with st.expander("Associations"):
                       st.write("Ici, tu trouveras les associations disponibles.")
                  with st.expander("Sites web et articles"):
                       st.write("Ici, tu trouveras des articles et des sites web qui parlent de la santé mentale.")

              with st.container():
                  st.subheader("Fonctionnalités interactives")
                  with st.expander("Défis quotidiens"):
                    st.write("Voici des petits défis à effectuer au quotidien.")
                  with st.expander("Communauté (modérée)"):
                    st.write("Voici un espace (modéré par des professionnels) où tu pourras partager ton experience.")
                  if centered_button("Refaire le questionnaire"):
                    st.session_state.page = "page_questionnaire"
                    st.session_state.results_displayed = False

              with st.container():
                  st.subheader("Personnalisation")
                  with st.expander("Recommandations personnalisées"):
                    st.write("Des recommandations personnalisées seront affichées.")
                  with st.expander("Rappels et Notifications"):
                    st.write("Permet de programmer des rappels pour tes exercices, la planification d'activités, ou pour reprendre contact avec un professionnel.")

          except Exception as e:
            st.error(f"Une erreur s'est produite lors de l'analyse des résultats: {e}")
        else:
          st.error("Le questionnaire n'est pas encore terminé")

        with st.container():
            # Afficher l'historique des résultats
            if st.session_state.get('historical_results') and not st.session_state.anonymous_mode:
                 st.subheader("Historique des résultats")
                 df = pd.DataFrame(st.session_state.historical_results)
                 st.dataframe(df)
            elif st.session_state.anonymous_mode :
                 st.write("**Vous utilisez le mode anonyme, vos résultats ne sont pas sauvegardés.**")
                 st.write("**L'historique de vos résultats n'est pas affiché.**")

        with st.container():
            st.write("En cas de besoin immédiat d'aide, vous pouvez demander une assistance en ligne.")
            if centered_button("Demander une assistance en ligne"):
               show_emergency_numbers()

        with st.container():
            # Afficher les ressources utiles
            st.subheader("Ressources Utiles")
            st.write("[Ligne d'écoute et soutien psychologique](https://www.sosamitie.org/)")
            st.write("[Centre de prévention du suicide](https://www.suicide-ecoute.fr/)")
            st.write("[Trouver un professionnel de santé mentale](https://annuaire.sante.fr/recherche/professionnels-sante-mentale)")

class YiriQuestionnaire:
    def __init__(self):
        self.questions = self.load_questions()
        self.responses = []
        self.current_question_index = 0
        self.scores = {}
        self.total_score = 0
        self.previous_responses = [] # Historique des réponses

    def load_questions(self):
       questions = [
            ("Vous sentez-vous souvent triste sans raison ?", ["Oui, très souvent", "Parfois", "Non, jamais"]),
            ("Avez-vous perdu l'intérêt pour les activités que vous aimiez ?", ["Oui", "Un peu", "Non"]),
           ("Avez-vous des troubles du sommeil ?", ["Oui, beaucoup", "Parfois", "Non"]),
           ("Vous sentez-vous souvent fatigué ?", ["Oui, tout le temps", "Parfois", "Non"]),
            ("Avez-vous des difficultés à vous concentrer ?", ["Oui", "Un peu", "Non"]),
            ("Ressentez-vous de la culpabilité ou de l'inutilité ?", ["Oui, fréquemment", "Parfois", "Non"]),
           ("Avez-vous des pensées négatives récurrentes ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Avez-vous des changements d'appétit ?", ["Oui", "beaucoup", "Un peu", "Non"]),
            ("Éprouvez-vous des difficultés à prendre des décisions ?", ["Oui", "Un peu", "Non"]),
            ("Vous sentez-vous isolé ou seul ?", ["Oui", "souvent", "Parfois", "Non"]),
           ("Ressentez-vous une perte d'énergie importante ?", ["Oui", "tout le temps", "Parfois", "Non"]),
            ("Avez-vous des pensées de mort ou de suicide ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous du mal à apprécier les moments de joie ?", ["Oui", "Parfois", "Non"]),
           ("Ressentez-vous une anxiété accrue ?", ["Oui", "très souvent", "Parfois", "Non"]),
           ("Avez-vous des douleurs physiques sans cause apparente ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des difficultés à vous lever le matin ?", ["Oui", "tout le temps", "Parfois", "Non"]),
            ("Avez-vous l'impression d'être un fardeau pour les autres ?", ["Oui", "souvent", "Parfois", "Non"]),
           ("Évitez-vous les interactions sociales ?", ["Oui", "fréquemment", "Parfois", "Non"]),
           ("Avez-vous des pertes de mémoire récentes ?", ["Oui", "Un peu", "Non"]),
            ("Avez-vous des variations d'humeur importantes ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Ressentez-vous un stress constant ?", ["Oui", "Parfois", "Non"]),
           ("Avez-vous l'impression que rien ne s'améliore ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Vous sentez-vous démotivé au travail ou dans vos études ?", ["Oui", "beaucoup", "Un peu", "Non"]),
            ("Avez-vous des maux de tête fréquents ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Avez-vous une perte d'estime de vous-même ?", ["Oui", "beaucoup", "Un peu", "Non"]),
            ("Avez-vous des pleurs fréquents ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Vous sentez-vous souvent irrité ou en colère ?", ["Oui", "Parfois", "Non"]),
           ("Avez-vous des difficultés à vous relaxer ?", ["Oui", "beaucoup", "Un peu", "Non"]),
           ("Ressentez-vous une pression constante ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des troubles digestifs récents ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous du mal à voir un avenir positif ?", ["Oui", "souvent", "Parfois", "Non"]),
           ("Ressentez-vous une baisse d'efficacité dans vos tâches quotidiennes ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des troubles respiratoires liés au stress ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des insomnies fréquentes ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Ressentez-vous un besoin de vous isoler ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Avez-vous des crises de panique ?", ["Oui", "fréquemment", "Parfois", "Non"]),
           ("Avez-vous des douleurs musculaires sans explication ?", ["Oui", "Parfois", "Non"]),
           ("Avez-vous des difficultés à vous exprimer ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Ressentez-vous une perte de motivation dans vos projets ?", ["Oui", "beaucoup", "Un peu", "Non"]),
            ("Avez-vous peur de l'avenir ?", ["Oui", "Parfois", "Non"]),
            ("Éprouvez-vous un sentiment de vide ?", ["Oui", "souvent", "Parfois", "Non"]),
            ("Avez-vous des difficultés à nouer des relations sociales ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des pensées pessimistes fréquentes ?", ["Oui", "souvent", "Parfois", "Non"]),
           ("Avez-vous des troubles de l'appétit ?", ["Oui", "souvent", "Parfois", "Non"]),
           ("Avez-vous des troubles de la libido ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des douleurs chroniques récentes ?", ["Oui", "Parfois", "Non"]),
           ("Vous sentez-vous dépassé par les événements ?", ["Oui", "Parfois", "Non"]),
           ("Avez-vous des tremblements ou des sueurs liées au stress ?", ["Oui", "Parfois", "Non"]),
            ("Avez-vous des palpitations cardiaques récentes ?", ["Oui", "Parfois", "Non"])
        ]
       random.shuffle(questions)
       return questions

    def ask_question(self, index):
        question, options = self.questions[index]
        st.write(f"**Question {index + 1}:** {question}")

        # Afficher l'option sélectionnée précédemment si elle existe
        if index < len(self.previous_responses):
            default_index = options.index(self.previous_responses[index])
        else:
            default_index = None

        self.current_response = centered_radio("Choisissez une réponse :", options, key=f"q{index}", index = default_index)

    def ask_questions(self, progress_bar):
      total_questions = len(self.questions)

      if self.current_question_index < total_questions:
        if self.current_question_index > 0 and self.current_question_index % 10 == 0 and not st.session_state.pause_requested:
           centered_markdown("Prenez une petite pause, buvez un verre d'eau ou faites quelques pas.")

           st.session_state.pause_requested = True
           if centered_button("Continuer le questionnaire"):
             st.session_state.pause_requested = False
        else:
            self.ask_question(self.current_question_index)

            col1, col2 = st.columns(2)

            with col1 :
               if centered_button("Précédent", key=f"btn_prev{self.current_question_index}", disabled= self.current_question_index == 0):
                  if self.current_question_index > 0:
                       self.current_question_index -= 1
                       if self.current_question_index < len(self.responses):
                           self.responses.pop()
                       progress_percent = (self.current_question_index / total_questions)
                       progress_bar.progress(progress_percent)
                       st.session_state.rerun_key += 1

            with col2:
                if centered_button("Suivant", key=f"btn{self.current_question_index}"):
                    if self.current_response:
                       if self.current_question_index < len(self.responses):
                           self.responses[self.current_question_index] = self.current_response
                       else:
                           self.responses.append(self.current_response)

                       self.previous_responses = self.responses.copy()
                       self.current_question_index += 1
                       progress_percent = (self.current_question_index / total_questions)
                       progress_bar.progress(progress_percent)
                       st.session_state.rerun_key += 1

                    else:
                       st.warning("Veuillez choisir une réponse avant de continuer.")

      else:
          centered_markdown("Vous avez terminé le questionnaire.")

    def is_completed(self):
        return self.current_question_index >= len(self.questions)

    def analyze_responses(self) -> Tuple[str, str, int]:
         """Analyse les réponses et retourne un résultat, une recommandation et le score total."""
         total_score = 0
         for index, response in enumerate(self.responses):
            question, options = self.questions[index]
            if response == options[0]:
                 total_score += 3
            elif response == options[1]:
                 total_score += 1
            elif response == options[2]:
                total_score += 0
         if total_score >= 30:
           result = "Signes de dépression sévère"
           recommendation = "Il est important de consulter un professionnel immédiatement."
         elif total_score >= 15:
            result = "Signes de dépression modérée"
            recommendation = "Consultez un professionnel pour discuter de vos symptômes."
         elif total_score >= 8:
            result = "Légers signes de dépression"
            recommendation = "Surveillez votre état et n'hésitez pas à consulter en cas d'aggravation."
         else:
             result = "Pas de signe de dépression"
             recommendation = "Continuez à prendre soin de vous."
         self.total_score = total_score
         return result, recommendation, total_score


    def save_results_to_csv(self):
        """Enregistre les résultats dans un fichier CSV."""
        file = io.StringIO()
        df = pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Score": self.total_score}])
        df.to_csv(file, index=False)
        st.download_button("Télécharger les résultats", file.getvalue(), "results.csv")

def create_pdf_report(result: str, recommendation: str, total_score: int, last_result: Dict[str, Any]) -> bytes:
    """Crée un rapport PDF."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Rapport du Questionnaire Yiri", ln=True, align='C')
    pdf.cell(200, 10, txt=f"Date: {last_result['Date']}", ln=True)
    pdf.cell(200, 10, txt=f"Résultats: {result}", ln=True)
    pdf.cell(200, 10, txt=f"Recommandations: {recommendation}", ln=True)
    pdf.cell(200, 10, txt=f"Score total: {total_score}", ln=True)
    return pdf.output(dest="S").encode("latin-1")

def send_email(email: str, result: str, recommendation: str, total_score: int, last_result: Dict[str, Any]):
    """Envoie un email avec les résultats."""
    sender_email = "your_email@example.com"  # Remplace par ton adresse email
    sender_password = "your_email_password"  # Remplace par ton mot de passe email
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = "Résultats du Questionnaire Yiri"

    body = f"""
    Voici les résultats du questionnaire Yiri que vous avez complété :

    Date: {last_result['Date']}
    Résultats: {result}
    Recommandations: {recommendation}
    Score total: {total_score}
    """
    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.example.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.send_message(message)
        server.quit()
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email : {e}")

def show_emergency_numbers():
    st.write("Pour obtenir de l'aide immédiate, contactez les numéros suivants :")
    st.write("Numéro d'urgence : 112")
    st.write("Soutien à la santé mentale : 0800 123 123")

# --- Lancement de l'application ---
def main():
    if st.session_state.page == "page_bienvenue":
        page_bienvenue()
    elif st.session_state.page == "page_conditions":
        page_conditions()
    elif st.session_state.page == "page_accueil":
        page_accueil()
    elif st.session_state.page == "page_questionnaire":
        page_questionnaire()
    elif st.session_state.page == "page_resultats":
        page_resultats()

if __name__ == "__main__":
    main()