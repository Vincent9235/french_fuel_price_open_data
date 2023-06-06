import streamlit as st

# Page config
st.set_page_config(
    page_title='Explanations',
    page_icon='🗒️',
    layout='wide',
    menu_items={
        'Get Help': 'https://www.extremelycoolapp.com/help',
        'Report a bug': "https://www.extremelycoolapp.com/bug",
        'About': "# This is a header. This is an *extremely* cool app!"
    })

# Side bar
with st.sidebar:
    st.header('Informations on author')
    st.markdown('**Vincent Laurens💻**')
    st.write('📈Data Scientist at Bouygues Construction IT | Data Management student🏫') 
    st.write("""<div style="width:100%;text-align:center;"><a href="https://www.linkedin.com/in/vincentlaurenspro" style="float:center"><img src="https://img.shields.io/badge/Vincent%20Laurens-0077B5?style=for-the-badge&logo=linkedin&logoColor=white&link=https://www.linkedin.com/in/vincentlaurenspro/%22" width="100%" height="50%"></img></a></div>""", unsafe_allow_html=True)

# Page title
st.title('Explanations')

# How to reach me 
st.header('How to reach me')
st.write('You can reach me on [LinkedIn](https://www.linkedin.com/in/vincentlaurenspro/) or see my [GitHub](https://github.com/Vincent9235).')

# Contact form
def main():
    st.title("Contact me")

    # Champs du formulaire
    nom = st.text_input("Name")
    email = st.text_input("Email")
    message = st.text_area("Message")

    # Bouton pour soumettre le formulaire
    if st.button("Send"):
        # Vérification des champs obligatoires
        if nom and email and message:
            # Envoyer le formulaire ou effectuer une action supplémentaire
            # (par exemple, enregistrement dans une base de données, envoi d'un email, etc.)
            st.success("Formulaire envoyé avec succès!")
        else:
            st.error("Veuillez remplir tous les champs obligatoires.")

if __name__ == '__main__':
    main()