import streamlit as st
import requests
import os
from langchain import OpenAI
from langchain.llms import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate

os.environ['OPENAI_API_KEY'] = st.secrets["OPENAI_API_KEY"]

llm = OpenAI(temperature=0.9, max_tokens=3000) 

destination_choice_template = PromptTemplate(
        input_variables = ['activity', 'weather', 'budget', 'region'], 
        template='''Give a travel suggestion based on the user preferences.
                Write the travel suggestion in the beginning followed by a dot.
                Preferred user activity: {activity}
                Preferred user weather: {weather}
                User budget: {budget}
                Region: {region}
                Example outputs: Crete. Enjoy the Mediterranean sun while relaxing on the beach 
                or exploring the many small villages and vibrant cities. With its affordable accommodation 
                and beautiful scenery, it's the perfect getaway.
                Output: '''
)
destination_chain = LLMChain(llm=llm, prompt=destination_choice_template, verbose=True)

travel_plan_template = PromptTemplate(
        input_variables = ['destination', 'activity', 'budget', 'duration', 'company', 'musea', 'restaurants'], 
        template='''Plan a holiday for the user. The user would like to travel to {destination} for {duration} days.
                The user prefers {activity} during his holidays. Budgetwise the holiday should be {budget}. 
                The user travels with {company}. The user wants to visit musea {musea} and go to restaurants {restaurants}.
                Output: '''
)
travel_plan_chain = LLMChain(llm=llm, prompt=travel_plan_template, verbose=True)

UNSPLASH_ACCESS_KEY = "N32U7pEUquy3St4VmmFc4yiflRA_20meLsF5DsZdqcg"
UNSPLASH_API_URL = "https://api.unsplash.com/photos/random"

def get_image_url(query):
    params = {
        "query": query,
        "orientation": "landscape",
        "client_id": UNSPLASH_ACCESS_KEY
    }
    response = requests.get(UNSPLASH_API_URL, params=params)
    if response.status_code == 200:
        result = response.json()
        return result["urls"]["regular"]
    else:
        return None

def main():
    st.title("GPTravel - Holiday Planer :beach_with_umbrella:")
    if 'destination' not in st.session_state:
        st.session_state['destination'] = ""
    option = st.radio('Choose your option:', ("I already have a destination and I only want to plan my trip", "I want to find a travel destination and plan my trip"))
    if option == "I want to find a travel destination and plan my trip":
        activity = st.selectbox("Select preferred activity", ["Relaxing", "Exploring", "Sightseeing", "Sportive", "Educational"])
        weather = st.selectbox("Select preferred weather", ["Tropical", "Mediterranean", "Temperate", "Cold"])
        budget = st.selectbox("Select budget", ["Expensive", "Moderate", "Affordable", "Zero budget"])
        region = st.selectbox("Select region", ["Europe", "North America", "South America", "Africa", "Middle East", "Asia", "Oceania"])

        if st.button("Find Destinations"):
            response = destination_chain.run(activity=activity, weather=weather, budget=budget, region=region)
            st.write(response)
            destination = response.split(".")[0]
            st.session_state['destination'] = destination
            st.session_state['activity'] = activity
            st.session_state['budget'] = budget
            image_url = get_image_url(destination)
            if image_url:
                st.image(image_url, caption=destination, use_column_width=True)
    
    else:
        destination = st.text_input("What is your destination?")
        activity = st.selectbox("Select preferred activity", ["Relaxing", "Exploring", "Sightseeing", "Sportive", "Educational"])
        budget = st.selectbox("Select budget", ["Expensive", "Moderate", "Affordable", "Zero budget"])
        if st.button("Save preferences"):
            st.session_state['destination'] = destination
            st.session_state['activity'] = activity
            st.session_state['budget'] = budget
            image_url = get_image_url(destination)
            if image_url:
                st.image(image_url, caption=destination, use_column_width=True)

    if st.session_state['destination'] != "":
        st.write("Plan your trip")
        duration = st.slider("How many days are you traveling", 1, 28, 7)
        company = st.selectbox("Who are you traveling with?", ["Alone", "Partner", "Friends", "Family"])
        musea = st.selectbox("How often do you want to visit musea?", ["Often", "Sometimes", "Never"])
        restaurants = st.selectbox("How often do you want to go to restaurants?", ["Often", "Sometimes", "Never"])
        if st.button("Plan your trip"):
            response = travel_plan_chain.run(destination=st.session_state['destination'], activity=st.session_state['activity'], budget=st.session_state['budget'], duration=duration, company=company, musea=musea, restaurants=restaurants)
            st.write(response)



if __name__ == "__main__":
    main()
