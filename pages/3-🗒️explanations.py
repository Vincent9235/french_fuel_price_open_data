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
st.title('Explanations🗒️')

# About the app
st.header('About the app')
st.write('This app is a dashboard that allows you to visualize statistics on fuel stations in France. It is based on the data provided by the French government on the [Open Data Plateform](https://www.data.gouv.fr/fr/datasets/prix-des-carburants-en-france/). Thanks to this app, user can see differents statistics about fuel price in France. For example, he can see : ')
st.markdown("""
- The average price of fuel in France today, over 30 days and over 6 months
- Search the nearest fuel station from his location
- Find the most expensive petrol distributor in France
- Find the cheapest petrol distributor in France
""")
st.write('These differents graphics allows the user to save money and see the global trend in petrol prices. The increase in petrol prices in the current period of inflation is a real social issue. Re-using the data provided by the government can be a real help to us all in our day-to-day lives.')

# Personal feeling and feedback
st.header('Personal feeling and feedback') 
st.write('This app is not perfect. I met many difficulties during the development of this app. I had to learn a lot of new things. For example, I\'m not used to using python to process my data. I generally use SQL.')
st.write('I also use many datasets with differents formats. I had never used the XML format before.')
st.write(' In addition, the history data was not structured in the same way as the API provided by the government. I also had to rework the json file for service station brands, which was incorrectly formatted.')
st.write('I learned a lot during the development of this application and I\'m delighted. When I have some free time I won\'t hesitate to go back to the project to improve it.')
st.write('Feel free to reuse my app and my code to create your own app. I would be happy to see your work.')

# How to reach me 
st.header('How to reach me')
st.write('You can reach me on [LinkedIn](https://www.linkedin.com/in/vincentlaurenspro/) or see my [GitHub](https://github.com/Vincent9235).')