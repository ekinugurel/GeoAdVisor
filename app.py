import streamlit as st
from datetime import time


# TODO add SessionState to the code below so that it the page refreshes only when we hit generate map button.
class App:
    def __init__(self, request_handler):
        self.request_handler = request_handler

    def run(self):
        st.title('GeoAdVisor')
        st.subheader('Select specifications:')
        ########

        class_selectbox = st.selectbox('Select the classification of advertisement:', ('Dining', 'Grocery', 'Clothing'))
        time_selectbox = st.selectbox('What is your desired timeframe? ', ('Real-time', 'historical'))
        if time_selectbox=='historical':
            selected_time = st.slider( "Select your time frame:", value=(time(12, 00)))
        else:
            selected_time = None
        generate = st.button('Generate Map')
        #########

        if generate:
            st.subheader('Results:')
            with st.spinner("Loading..."):
                # todo are we gonna read shapefiles here or in the logic?
                map_data = self.request_handler.send_request(class_selectbox, selected_time)
            st.success("Done!")
            st.map(map_data)

            download_button= st.sidebar.button('Generate .csv file')
            if download_button:
                with st.sidebar:
                    csv_data = map_data.to_csv(index=False)
                    st.success("csv file generated...")
                    # Provide the download link
                    st.download_button(
                        label="Download CSV file",
                        data=csv_data,
                        file_name=f'GeoAdVisor_{class_selectbox}_time{selected_time}.csv',
                        key='download_button'
                    )









