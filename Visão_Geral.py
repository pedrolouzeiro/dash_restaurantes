import pandas as pd
import streamlit as st
import folium
from streamlit_folium import folium_static
from folium.plugins import MarkerCluster

df = pd.read_csv('dataset/zomato.csv')


paises = {
    'Country Code': [1,14,30,37,94,148,162,166,184,189,191,208,214,215,216],
    'Country':["India","Australia","Brazil","Canada","Indonesia","New Zeland","Philippines","Qatar","Singapure","South Africa","Sri Lanka","Turkey","United Arab Emirates","England","United States of America"]
}
paises=pd.DataFrame(paises)

df['Price range']= df['Price range'].replace({1: "cheap"})
df['Price range']= df['Price range'].replace({2: "normal"})
df['Price range']= df['Price range'].replace({3: "expensive"})
df['Price range']= df['Price range'].replace({4: "gourmet"})

cores = {
    'Rating color' : ["3F7E00","5BA829","9ACD32","CDD614" ,"FFBA00" ,"CBCBC8" ,"FF7800"],
    'R Color' : ["darkgreen","green","lightgreen","orange","red","darkred","darkred"]
}
cores= pd.DataFrame(cores)

df = pd.merge(df, cores, on='Rating color', how='inner')
df = pd.merge(df, paises, on='Country Code', how='inner')


df.drop(columns=['Address', 'Locality','Locality Verbose','Country Code'], inplace=True)

df.drop_duplicates(keep='first', inplace=True) 
df.dropna(inplace=True)

df['Cuisines'] = df.loc[:,'Cuisines'].apply(lambda x: x.split(",")[0])
#
#Layout
#
st.set_page_config(page_title="Home", layout='wide') 

with st.container():
    
    col1,col2,col3,col4,col5 = st.columns(5)
    
    with col1:
        col1.metric(label='Restaurantes Cadastrados', value=len(df['Restaurant ID'].unique()))
    with col2:
        col2.metric(label='Países Cadastrados', value=len(df['Country'].unique()))
    with col3:
        col3.metric(label='Cidades Cadastradas', value=len(df['City'].unique()))
    with col4:
        col4.metric(label='Avaliações Feitas', value=df['Votes'].sum())
    with col5:
        col5.metric(label='Tipos de Culinária', value=df['Cuisines'].nunique())
        
        
    
    f = folium.Figure(width=1920, height=1080)

    m = folium.Map(max_bounds=True,tiles="cartodb positron").add_to(f)
    m.save("footprint.html")
    marker_cluster = MarkerCluster().add_to(m)

    for _, line in df.iterrows():

        name = line["Restaurant Name"]
        price_for_two = line["Average Cost for two"]
        cuisine = line["Cuisines"]
        currency = line["Currency"]
        rating = line["Aggregate rating"]
        color = f'{line["R Color"]}'

        html = "<p><strong>{}</strong></p>"
        html += "<p>Price: {},00 ({}) para dois"
        html += "<br />Type: {}"
        html += "<br />Aggragate Rating: {}/5.0"
        html = html.format(name, price_for_two, currency, cuisine, rating)

        popup = folium.Popup(
            folium.Html(html, script=True),
            max_width=500,
        )

        folium.Marker(
            [line["Latitude"], line["Longitude"]],
            popup=popup,
            icon=folium.Icon(color=color, icon="home", prefix="fa"),
        ).add_to(marker_cluster)
    st.write('Localização dos Restaurantes')    
    folium_static(m, width=1200, height=400)