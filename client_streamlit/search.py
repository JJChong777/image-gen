import streamlit as st
from modules import display_img_with_download_thumbnail, make_safe_img_get, RequestType

def search_images(query):
    # Simulated search result
    return [
        ("F16 Jet 1", "https://upload.wikimedia.org/wikipedia/commons/1/1a/YF-16_and_YF-17_in_flight.jpg"),
        ("F16 Jet 2", "https://upload.wikimedia.org/wikipedia/commons/1/15/F16A_FAP_linksup_KC-10.jpg"),
        ("F16 Jet 3", "https://upload.wikimedia.org/wikipedia/commons/c/c4/F16_SCANG_InFlight.jpg"),
        ("F16 Jet 4", "https://upload.wikimedia.org/wikipedia/commons/c/c9/F-16_June_2008.jpg"),
        ("F16 Jet 5", "https://upload.wikimedia.org/wikipedia/commons/0/05/F-16_CJ_Fighting_Falcon.jpg"),
        ("F16 Jet 6", "https://upload.wikimedia.org/wikipedia/commons/4/45/A_U.S._Air_Force_Airman_from_the_169th_Fighter_Wing_conducts_post_flight_tasks_in_an_F-16_Fighting_Falcon_aircraft_during_a_phase_II_operational_readiness_evaluation_at_McEntire_Joint_National_Guard_Base%2C_S.C._080412-F-WT236-013.jpg"),
        ("F16 Jet 7", "https://upload.wikimedia.org/wikipedia/commons/d/dc/F-16_takeoff_in_Germany.jpg"),
        ("F16 Jet 8", "https://upload.wikimedia.org/wikipedia/commons/7/79/F-16-Netz-107-fighter-and-killmarks-01.jpg"),
        ("F16 Jet 9", "https://upload.wikimedia.org/wikipedia/commons/a/a9/F16_-_RIAT_2014_%2834306872320%29.jpg"),
        ("F16 Jet 10", "https://upload.wikimedia.org/wikipedia/commons/1/10/An_F-16_of_the_Egyptian_Air_Force_fly_in_support_of_exercise_Agile_Phoenix.jpg"),
        ("F16 Jet 11", "https://upload.wikimedia.org/wikipedia/commons/4/4e/F-16_UAF_%28cropped%29.jpg"),
        ("F16 Jet 12", "https://upload.wikimedia.org/wikipedia/commons/c/cf/Iraqi_Air_Force_F-16_Fighting_Falcon_flies_over_an_undisclosed_location_July_18_2019.jpg"),
        ("F16 Jet 13", "https://upload.wikimedia.org/wikipedia/commons/a/a2/ROCAF_F-16B_6826_Taxiing_at_Hualien_Air_Force_Base_20170923b.jpg"),
    ]

def main():
    st.title("Search Existing Images")
    submitted = False
    with st.form("suggested_question_form"):
        initial_query = st.text_input(
            "Search image database",
            value="F16 Airplane",
        )
        submitted = st.form_submit_button('Search Images')
    if submitted:
        st.write(f"Showing results for: **{initial_query}**")
        results = search_images(initial_query)
        
        cols = st.columns(3)
        for i, (name, url) in enumerate(results):
            with cols[i % 3]:
                success, img_response = make_safe_img_get(url)
                if success:
                    display_img_with_download_thumbnail(img_response, name)
                else:
                    st.error(img_response)


if __name__ == "__main__":
    main()