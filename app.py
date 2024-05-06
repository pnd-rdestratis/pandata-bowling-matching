import streamlit as st
import backend
import os
import base64

def main():
    st.image("logo.png", width=150)
    st.title('AI Team Matching')

    with st.expander("Add New Player", expanded=False):
        with st.form("Add Player Form", clear_on_submit=True):
            vorname = st.text_input("Vorname")
            nachname = st.text_input("Nachname")
            lieblingsdrink = st.text_input("Lieblingsdrink")
            lieblingshobby = st.text_input("Lieblingshobby")
            branche = st.text_input("Branche")
            submitted = st.form_submit_button("Add Player")
            if submitted:
                backend.add_player(vorname, nachname, lieblingsdrink, lieblingshobby, branche)
                st.success("Player added successfully!")

    if st.button('Generate Teams'):
        with st.spinner('Generating Teams...'):
            teams = backend.generate_teams()
            display_teams(teams)

def get_base64(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def set_background(png_file):
    bin_str = get_base64(png_file)
    page_bg_img = '''
    <style>
    .stApp {
    background-image: url("data:image/png;base64,%s");
    background-size: cover;
    }
    </style>
    ''' % bin_str
    st.markdown(page_bg_img, unsafe_allow_html=True)


def display_teams(teams):
    if not teams:
        st.write("No teams generated.")
        return

    for team in teams['teams']:
        st.header(team['team_name'])
        st.subheader("Players:")
        for player in team['players']:
            st.write(f"{player['first_name']} {player['last_name']}")
        st.subheader("Matching Reason:")
        st.write(team['matching_reason'])

        # Show spinner while generating and loading the logo
        with st.spinner('Generating logo...'):
            logo_url = backend.generate_logo(team['team_name'], team['matching_reason'])
            if logo_url:
                st.image(logo_url, caption='Team Logo')
            else:
                st.error("Failed to generate logo.")

        st.write("---")


if __name__ == "__main__":
    set_background("bg3.png")
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
    main()
