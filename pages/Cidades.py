import pandas as pd
import streamlit as st
import plotly.express as px
import numpy as np
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
st.set_page_config(page_title="Cidades", layout='wide') 
tab1, tab2 = st.tabs(["Planejamento", "Estratégia"])

with tab1:
    with st.container():
        df_aux=df[['City', 'Cuisines']].groupby(['City','Cuisines'])['Cuisines'].count().to_frame('count').reset_index()

        fig = px.treemap(df_aux, path=['City', 'Cuisines'], values='count', title='Tipos de Culinária Populares por Cidade')
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        fig.data[0].textinfo = 'label+text+value'
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        with col1:
            custo_pra_dois=df[['City','Average Cost for two']].groupby(['City'])['Average Cost for two'].mean().reset_index().sort_values('Average Cost for two', ascending=False).head(15)
            fig = px.bar(
                custo_pra_dois, 
                x="Average Cost for two", 
                y="City", 
                text='Average Cost for two',
                title='Cidades com Maior Custo P/ Dois' ,
                labels={
                                'City': ' ',
                                'Average Cost for two' : ' '
                }
            )
            fig.update_traces(texttemplate='%{text:.2f}')
            fig.update_xaxes(showticklabels=False,showgrid=False)
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avaliacao_por_cidade = df[['City', 'Aggregate rating']].groupby(['City'])['Aggregate rating'].mean().reset_index().sort_values('Aggregate rating', ascending=False).head(15)
            fig = px.bar(
                avaliacao_por_cidade, 
                x="Aggregate rating", 
                y="City", 
                text='Aggregate rating',
                title='Melhores Médias de Avaliação por Cidade' ,
                labels={
                                'City': ' ',
                                'Aggregate rating' : ' '
                }
            )
            fig.update_traces(texttemplate='%{text:.2f}')
            fig.update_xaxes(showticklabels=False,showgrid=False)
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
            
        with col3:
            avaliacao_por_cidade = df[['City', 'Aggregate rating']].groupby(['City'])['Aggregate rating'].mean().reset_index().sort_values('Aggregate rating').head(15)
            fig = px.bar(
                avaliacao_por_cidade, 
                x="Aggregate rating", 
                y="City", 
                text='Aggregate rating',
                title='Piores Médias de Avaliação por Cidade' ,
                labels={
                                'City': ' ',
                                'Aggregate rating' : ' '
                }
            )
            fig.update_traces(texttemplate='%{text:.2f}')
            fig.update_xaxes(showticklabels=False,showgrid=False)
            fig.update_layout(yaxis={'categoryorder':'total descending'}, height=600)

            st.plotly_chart(fig, use_container_width=True)
            
            
with tab2:
    option = st.selectbox("", ["O que deseja analisar?","Crescimento", "Competição","Custo Benefício","Capacidade de Atendimento"])

    if option == "Crescimento":
        crescimento=df[['City','Aggregate rating']].groupby(['City'])[['Aggregate rating','City']].agg({'City': 'count','Aggregate rating': 'mean'}).rename(columns={'City':'count'}).reset_index()
#fig = px.scatter(competicao, x="count", y="Aggregate rating")
        crescimento.columns = ['City', 'Number of Restaurants', 'Average Rating']
        fig = px.scatter(
                    crescimento,
                    x='Number of Restaurants',
                    y='Average Rating',
                    text='City',
                    title='Potencial de Crescimento: Número de Restaurantes vs Avaliação Média por Cidade',
                    labels={
                        'Number of Restaurants': 'Número de Restaurantes',
                        'Average Rating': 'Avaliação Média'
                    },
                    height=600,
                    template='plotly',
                    hover_data={'City': True}
        )
        fig.add_shape(
                    type='line',
                    x0=crescimento['Number of Restaurants'].min()+39, x1=crescimento['Number of Restaurants'].max()/2,
                    y0=crescimento['Average Rating'].min()-0.1, y1=crescimento['Average Rating'].max() + 0.1,
                    line=dict(dash='dash', color='Red')
        )

        fig.add_shape(
                    type='line',
                    x0=crescimento['Number of Restaurants'].min()-1, x1=crescimento['Number of Restaurants'].max() +1,
                    y0=3.5, y1= 3.5,
                    line=dict(dash='dash', color='Green')
        )

        fig.add_annotation(
                    x=20, y=4.3,
                    text='Oportunidade de Expansão', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=60, y=4.3,
                    text='Mercado Sólido e Competitivo', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=20, y=2.5,
                    text='Mercado Desafiador', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=60, y=2.5,
                    text='Necessidade de melhorias', 
                    showarrow=False, 
                    font=dict(size=20)
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom right')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alta Avaliação, Muitos Restaurantes:
            Mercado Sólido e Competitivo: Cidades com muitos restaurantes bem avaliados, indicando um mercado maduro e competitivo.
            
        -Alta Avaliação, Poucos Restaurantes:
            Oportunidade de Expansão: Cidades com poucas opções de restaurantes, mas altas avaliações, sugerem um alto potencial para novos negócios que mantenham a qualidade.
            
        -Baixa Avaliação, Muitos Restaurantes:
            Necessidade de Melhoria: Cidades com muitos restaurantes e avaliações baixas, indicando uma saturação de mercado, mas com grandes oportunidades para melhorias de qualidade.
            
        -Baixa Avaliação, Poucos Restaurantes:
            Mercado Desafiador: Cidades com poucos restaurantes e avaliações baixas, mostrando um mercado de alto risco e baixo potencial.
     
'''
        )

    elif option == "Competição":
        
        competicao=df[['City','Aggregate rating']].groupby(['City'])[['Aggregate rating','City']].agg({'City': 'count','Aggregate rating': 'mean'}).rename(columns={'City':'count'}).reset_index()
#fig = px.scatter(competicao, x="count", y="Aggregate rating")
        competicao.columns = ['City', 'Number of Restaurants', 'Average Rating']
        fig = px.scatter(
                    competicao,
                    x='Number of Restaurants',
                    y='Average Rating',
                    text='City',
                    title='Análise de Competição: Número de Restaurantes vs Avaliação Média por Cidade',
                    labels={
                        'Number of Restaurants': 'Número de Restaurantes',
                        'Average Rating': 'Avaliação Média'
                    },
                    height=600,
                    template='plotly',
                    hover_data={'City': True}
        )
        fig.add_shape(
                    type='line',
                    x0=competicao['Number of Restaurants'].min()+39, x1=competicao['Number of Restaurants'].max()/2,
                    y0=competicao['Average Rating'].min()-0.1, y1=competicao['Average Rating'].max() + 0.1,
                    line=dict(dash='dash', color='Red')
        )

        fig.add_shape(
                    type='line',
                    x0=competicao['Number of Restaurants'].min()-1, x1=competicao['Number of Restaurants'].max() +1,
                    y0=3.5, y1= 3.5,
                    line=dict(dash='dash', color='Green')
        )

        fig.add_annotation(
                    x=20, y=4.3,
                    text='Mercado Emergente', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=60, y=4.3,
                    text='Forte Competição', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=20, y=2.5,
                    text='Alto Risco', 
                    showarrow=False, 
                    font=dict(size=20)
        )
        fig.add_annotation(
                    x=60, y=2.5,
                    text='Muitos Concorrentes e Baixa Qualidade', 
                    showarrow=False, 
                    font=dict(size=15)
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom right')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alta Avaliação, Muitos Restaurantes:
            Forte Competição: Cidades com um grande número de restaurantes e altas avaliações, indicando um mercado competitivo onde a qualidade é essencial para manter a posição.
            
        -Alta Avaliação, Poucos Restaurantes:
            Mercado Emergente: Cidades com poucas opções de restaurantes, mas altas avaliações, sugerem um mercado emergente com grande potencial para novos estabelecimentos de alta qualidade.
            
        -Baixa Avaliação, Muitos Restaurantes:
            Muitos Concorrentes e Baixa Qualidade: Cidades com muitos restaurantes e avaliações baixas, indicando que há muitos concorrentes, mas uma necessidade de melhoria na qualidade geral.
            
        -Baixa Avaliação, Poucos Restaurantes:
            Alto Risco: Cidades com poucos restaurantes e avaliações baixas, mostrando um mercado de alto risco para novos investimentos.
     
'''
        )
    
    
    elif option == "Custo Benefício":
        custo_vs_avaliação_por_cidade=df[['City','Aggregate rating','Average Cost for two']].groupby(['City'])[['Aggregate rating','Average Cost for two']].mean().reset_index()

        fig = px.scatter(
                    custo_vs_avaliação_por_cidade, 
                    x="Average Cost for two", 
                    y="Aggregate rating",
                    text='City',
                    title='Custo Para Dois vs Avaliação Média por País',
                    labels={
                        'Average Cost for two': 'Custo P/ Dois',
                        'Aggregate rating': 'Avaliação Média'
                    },
                    height=600,
                    template='plotly',
                    hover_data={'City': True}
        )
        fig.add_shape(
                    type='line',
                    x0=(custo_vs_avaliação_por_cidade['Average Cost for two'].max() / 2)-custo_vs_avaliação_por_cidade['Average Cost for two'].min(), x1=custo_vs_avaliação_por_cidade['Average Cost for two'].max() / 2,
                    y0=custo_vs_avaliação_por_cidade['Aggregate rating'].min()- 0.1, y1=custo_vs_avaliação_por_cidade['Aggregate rating'].max()+0.1,
                    line=dict(dash='dash', color='Red'),
                )

        fig.add_shape(
                    type='line',
                    x0=custo_vs_avaliação_por_cidade['Average Cost for two'].min(), x1=custo_vs_avaliação_por_cidade['Average Cost for two'].max()+1000,
                    y0=(custo_vs_avaliação_por_cidade['Aggregate rating'].max() + custo_vs_avaliação_por_cidade['Aggregate rating'].min()) / 2, y1=(custo_vs_avaliação_por_cidade['Aggregate rating'].max() + custo_vs_avaliação_por_cidade['Aggregate rating'].min()) / 2,
                    line=dict(dash='dash', color='Green'),
                )
        fig.add_annotation(
                    x=320000, y=4.3,
                    text='Valor Alto e Boa Avaliação', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(            
                    x=100000, y=4.3,
                    text='Bom Valor e Boa Avaliação', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(
                    x=320000, y=2.5,
                    text='Caro e Baixa Avaliação', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(

                    x=100000, y=2.5,
                    text='Bom Valor e Baixa Avaliação', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.update_xaxes(showgrid=False, autorange='reversed')
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom right')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alto Custo, Alta Avaliação:
            Valor Alto e Boa Avaliação: Cidades onde os restaurantes são caros, mas bem avaliados, indicando que os clientes percebem um alto valor na qualidade oferecida.
            
        -Alto Custo, Baixa Avaliação:
            Caro e Baixa Avaliação: Cidades onde os restaurantes são caros e mal avaliados, sugerindo uma percepção negativa do valor oferecido e necessidade de revisão de preço ou qualidade.
            
        -Baixo Custo, Alta Avaliação:
            Bom Valor e Alta Avaliação: Cidades com refeições baratas e bem avaliadas, indicando que os restaurantes estão entregando um bom valor pelo preço.
            
        -Baixo Custo, Baixa Avaliação:
            Bom Valor e Baixa Avaliação: Cidades onde os restaurantes são baratos, mas mal avaliados, sugerindo que a qualidade precisa ser melhorada para aumentar as avaliações.
     
'''
        )
    
    
    elif option == "Capacidade de Atendimento":
        capacidade_atendimento= df[['City','Has Table booking','Has Online delivery']].groupby(['City'])[['Has Table booking','Has Online delivery','City']].agg({'City': 'count','Has Table booking': 'sum','Has Online delivery': 'sum'}).rename(columns={'City':'count'}).reset_index()
        capacidade_atendimento['indice'] = (capacidade_atendimento['Has Table booking'] * 0.5 + capacidade_atendimento['Has Online delivery'] * 0.5)
        fig = px.scatter(
            capacidade_atendimento, 
            x="count", 
            y="indice",
            text='City',
            title='Capacidade de Atendimento: Número de Restaurantes vs Pontuação',
            labels={
                'count': 'Número de Resturantes',
                'indice': 'Pountuação'
            },
            height=600,
            template='plotly',
            hover_data={'City': True}
        )
        fig.add_shape(
                    type='line',
                    x0=capacidade_atendimento['count'].max() / 2 , x1=capacidade_atendimento['count'].max() / 2,
                    y0=capacidade_atendimento['indice'].min(), y1=capacidade_atendimento['indice'].max() +1,
                    line=dict(dash='dash', color='Red'),
                )

        fig.add_shape(
                    type='line',
                    x0=capacidade_atendimento['count'].min()-1, x1=capacidade_atendimento['count'].max() +1,
                    y0=capacidade_atendimento['indice'].max() / 2, y1=capacidade_atendimento['indice'].max() / 2,
                    line=dict(dash='dash', color='Green'),
                )
        fig.add_annotation(
                    x=19, y=35,
                    text='Oportunidade de Expansão', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(
                    x=60, y=35,
                    text='Serviço de Qualidade', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(
                    x=19, y=10,
                    text='Necessidade de Transformação', 
                    showarrow=False, 
                    font=dict(size=20)
                )
        fig.add_annotation(
                    x=60, y=10,
                    text='Necessita de Melhorias no Serviço', 
                    showarrow=False, 
                    font=dict(size=18)
                )
        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom right')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alta Capacidade de Atendimento, Alta Avaliação:
            Serviço de Qualidade: Cidades onde os restaurantes oferecem tanto reservas de mesa quanto entregas online e possuem altas avaliações, indicando um serviço completo que atende bem às necessidades dos clientes.
            
        -Alta Capacidade de Atendimento, Baixa Avaliação:
            Necessidade de Melhorias no Serviço: Cidades onde os restaurantes oferecem reservas de mesa e entregas online, mas têm avaliações baixas, indicando que, embora o serviço esteja disponível, a execução precisa de melhorias.
            
        -Baixa Capacidade de Atendimento, Alta Avaliação:
            Oportunidade de Expansão: Cidades bem avaliadas que não oferecem reservas de mesa ou entregas online, sugerindo uma oportunidade para expandir esses serviços e aumentar ainda mais a satisfação do cliente.
            
        -Baixa Capacidade de Atendimento, Baixa Avaliação:
            Necessidade de Transformação: Cidades onde os restaurantes não oferecem reservas de mesa nem entregas online e têm avaliações baixas, indicando um mercado que necessita de uma transformação significativa para se tornar competitivo.
     
'''
        )