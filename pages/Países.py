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
st.set_page_config(page_title="Países", layout='wide') 
tab1, tab2 = st.tabs(["Planejamento", "Estratégia"])

with tab1:
    with st.container():
        df_aux=df[['Country', 'Cuisines']].groupby(['Country','Cuisines'])['Cuisines'].count().to_frame('count').reset_index()

        fig = px.treemap(df_aux, path=['Country', 'Cuisines'], values='count', title='Tipos de Culinária Populares por País')
        fig.update_traces(root_color="lightgrey")
        fig.update_layout(margin = dict(t=50, l=25, r=25, b=25))
        fig.data[0].textinfo = 'label+text+value'
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)
        
        with col1:
            restaurantes_por_pais = df['Country'].value_counts().reset_index()
            fig = px.bar(
                restaurantes_por_pais, 
                x="count", 
                y="Country", 
                text='count',
                title='Distribuição de Restaurantes por País' ,
                
                labels={
                    'Country': ' ',
                    'count' : ' '
                }
            )
            fig.update_traces(texttemplate='%{text}')
            fig.update_xaxes(showticklabels=False,showgrid=False)
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            avaliacao_por_pais = df[['Country', 'Aggregate rating']].groupby(['Country'])['Aggregate rating'].mean().reset_index()
            fig = px.bar(
                avaliacao_por_pais, 
                x="Aggregate rating", 
                y="Country", 
                text='Aggregate rating',
                title='Média de Avaliação por País' ,
                labels={
                    'Country': ' ',
                    'Aggregate rating' : ' '
                }
            )
            fig.update_traces(texttemplate='%{text:.2f}')
            fig.update_xaxes(showticklabels=False,showgrid=False)
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=600)
            st.plotly_chart(fig, use_container_width=True)
            
with tab2:
    option = st.selectbox("", ["O que deseja analisar?","Crescimento", "Competição","Custo Benefício","Capacidade de Atendimento"])

    if option == "Crescimento":
        grouped_df = df.groupby('Country').agg({
        'Restaurant ID': 'count',
        'Aggregate rating': 'mean'
        }).reset_index()

        # Renomear colunas
        grouped_df.columns = ['Country', 'Number of Restaurants', 'Average Rating']

        # Criar o gráfico de dispersão com Plotly
        fig = px.scatter(
            grouped_df,
            x='Number of Restaurants',
            y='Average Rating',
            text='Country',
            title='Matriz de Crescimento: Número de Restaurantes vs Avaliação Média por País',
            labels={
                'Number of Restaurants': 'Número de Restaurantes',
                'Average Rating': 'Avaliação Média'
            },
            height=600,
            template='plotly',
            hover_data={'Country': True}
        )

        fig.add_shape(
            type='line',
            x0=grouped_df['Number of Restaurants'].min() * 19.44, x1=grouped_df['Number of Restaurants'].max() / 2,
            y0=grouped_df['Average Rating'].min() - 0.4, y1=grouped_df['Average Rating'].max() + 0.8,
            line=dict(dash='dash', color='Red')
        )

        fig.add_shape(
            type='line',
            x0=grouped_df['Number of Restaurants'].min() - 180, x1=grouped_df['Number of Restaurants'].max() + 100,
            y0=grouped_df['Average Rating'].median(), y1=grouped_df['Average Rating'].median(),
            line=dict(dash='dash', color='Green')
        )
        
        fig.add_annotation(
            x=650, y=4.8,
            text='Potencial de Crescimento', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=4.8,
            text='Forte Mercado Consolidado', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=650, y=3.6,
            text='Baixo Potencial/Alto Risco', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=3.6,
            text='Necessidade de Melhorias', 
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
            Forte Mercado Consolidado: Países onde a qualidade média dos restaurantes é alta e o número de estabelecimentos é grande. Indica um mercado maduro e competitivo, onde a excelência no serviço é mantida.
            
        -Alta Avaliação, Poucos Restaurantes:
            Potencial de crescimento: Países com alta avaliação média, mas com poucos restaurantes. O mercado tem um alto potencial para expansão, sugerindo que novos restaurantes podem ter sucesso se manterem a alta qualidade.
            
        -Baixa Avaliação, Muitos Restaurantes:
            Necessidade de melhorias: Países com muitos restaurantes, mas com avaliações baixas. Há uma saturação de mercado, mas os estabelecimentos precisam melhorar a qualidade para se destacar e atrair mais clientes.
            
        -Baixa Avaliação, Poucos Restaurantes:
            Baixo potencial/alto risco: Países com poucas opções de restaurantes e avaliações baixas. Indica um mercado desafiador, com alto risco de investimento devido à baixa qualidade percebida e baixa demanda.
     
'''
        )

    elif option == "Competição":
        
        competicao=df[['Country','Aggregate rating']].groupby(['Country'])[['Aggregate rating','Country']].agg({'Country': 'count','Aggregate rating': 'mean'}).rename(columns={'Country':'count'}).reset_index()
        fig = px.scatter(competicao, x="count", y="Aggregate rating")
        competicao.columns = ['Country', 'Number of Restaurants', 'Average Rating']

        # Criar o gráfico de dispersão com Plotly
        fig = px.scatter(
            competicao,
            x='Number of Restaurants',
            y='Average Rating',
            text='Country',
            title='Análise de Competição: Número de Restaurantes vs Avaliação Média por País',
            labels={
                'Number of Restaurants': 'Número de Restaurantes',
                'Average Rating': 'Avaliação Média'
            },
            height=600,
            template='plotly',
            hover_data={'Country': True}
        )

        fig.add_shape(
            type='line',
            x0=competicao['Number of Restaurants'].min() * 19.44, x1=competicao['Number of Restaurants'].max() / 2,
            y0=competicao['Average Rating'].min() - 0.4, y1=competicao['Average Rating'].max() + 0.8,
            line=dict(dash='dash', color='Red')
        )

        fig.add_shape(
            type='line',
            x0=competicao['Number of Restaurants'].min() - 180, x1=competicao['Number of Restaurants'].max() + 100,
            y0=competicao['Average Rating'].median(), y1= competicao['Average Rating'].median(),
            line=dict(dash='dash', color='Green')
        )

        
        fig.add_annotation(
            x=650, y=4.8,
            text='Oportunidade de Expansão', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=4.8,
            text='Mercado Sólido e Competitivo', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=650, y=3.6,
            text='Mercado Desafiador', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=3.6,
            text='Necessidade de melhorias', 
            showarrow=False, 
            arrowhead=1, 
            arrowsize=1, 
            arrowwidth=2, 
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
            Mercado Sólido e Competitivo: Esses países possuem muitos restaurantes com altas avaliações, indicando um mercado consolidado e altamente competitivo.
            
        -Alta Avaliação, Poucos Restaurantes:
            Oportunidade de Expansão: Países com poucas opções de restaurantes, mas altas avaliações, sugerem um alto potencial para expansão com foco na qualidade.
            
        -Baixa Avaliação, Muitos Restaurantes:
            Necessidade de Melhoria: Países com muitos restaurantes e avaliações baixas indicam uma saturação do mercado, mas com oportunidades significativas de melhoria na qualidade.
            
        -Baixa Avaliação, Poucos Restaurantes:
            Mercado Desafiador: Países com poucos restaurantes e avaliações baixas, mostrando um mercado de alto risco e baixo potencial.
     
'''
        )
    
    
    elif option == "Custo Benefício":
        custo_vs_avaliação_por_país=df[['Country','Aggregate rating','Average Cost for two']].groupby(['Country'])[['Aggregate rating','Average Cost for two']].mean().reset_index()
        custo_vs_avaliação_por_país[['Aggregate rating','Average Cost for two']] = np.round(custo_vs_avaliação_por_país[['Aggregate rating','Average Cost for two']],decimals=2)
        #Sem outliers
        custo_vs_avaliação_por_país.drop(custo_vs_avaliação_por_país.loc[custo_vs_avaliação_por_país['Average Cost for two'] == custo_vs_avaliação_por_país['Average Cost for two'].max()].index, inplace=True)


        fig = px.scatter(
            custo_vs_avaliação_por_país, 
            x="Average Cost for two", 
            y="Aggregate rating",
            text='Country',
            title='Custo Para Dois vs Avaliação Média por País',
            labels={
                'Average Cost for two': 'Custo P/ Dois',
                'Aggregate rating': 'Avaliação Média'
            },
            height=600,
            template='plotly',
            hover_data={'Country': True}
        )


        fig.add_shape(
            type='line',
            x0=(custo_vs_avaliação_por_país['Average Cost for two'].max() / 2)-custo_vs_avaliação_por_país['Average Cost for two'].min(), x1=custo_vs_avaliação_por_país['Average Cost for two'].max() / 2,
            y0=custo_vs_avaliação_por_país['Aggregate rating'].min(), y1=custo_vs_avaliação_por_país['Aggregate rating'].max(),
            line=dict(dash='dash', color='Red'),
        )

        fig.add_shape(
            type='line',
            x0=custo_vs_avaliação_por_país['Average Cost for two'].min(), x1=custo_vs_avaliação_por_país['Average Cost for two'].max(),
            y0=(custo_vs_avaliação_por_país['Aggregate rating'].max() + custo_vs_avaliação_por_país['Aggregate rating'].min()) / 2, y1=(custo_vs_avaliação_por_país['Aggregate rating'].max() + custo_vs_avaliação_por_país['Aggregate rating'].min()) / 2,
            line=dict(dash='dash', color='Green'),
        )
        
        fig.add_annotation(
            x=105000, y=4.2,
            text='Valor Alto e Boa Avaliação', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=36000, y=4.2,
            text='Bom Valor e Boa Avaliação', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=105000, y=3.6,
            text='Caro e Baixa Avaliação', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=36000, y=3.6,
            text='Bom Valor e Baixa Avaliação', 
            showarrow=False, 
            arrowhead=1, 
            arrowsize=1, 
            arrowwidth=2, 
            font=dict(size=20)
        )
        
        fig.update_xaxes(showgrid=False, autorange='reversed')
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom left')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alto Custo, Alta Avaliação:
            Valor Alto e Boa Avaliação: Países onde os restaurantes são caros, mas bem avaliados, indicando que os clientes percebem alto valor na qualidade oferecida.
            
        -Alto Custo, Baixa Avaliação:
            Caro e Baixa Avaliação: Países onde os restaurantes são caros e mal avaliados, sugerindo uma percepção negativa do valor oferecido e necessidade de revisão de preço ou qualidade.
            
        -Baixo Custo, Alta Avaliação:
            Bom Valor e Alta Avaliação: Países com refeições baratas e bem avaliadas, indicando que os restaurantes estão entregando um bom valor pelo preço.
            
        -Baixo Custo, Baixa Avaliação:
            Bom Valor e Baixa Avaliação: Países onde os restaurantes são baratos, mas mal avaliados, sugerindo que a qualidade ainda precisa ser melhorada para aumentar as avaliações.
     
'''
        )
    
    
    
    elif option == "Capacidade de Atendimento":
        capacidade_atendimento = df[['Country','Has Table booking','Has Online delivery']].groupby(['Country'])[['Has Table booking','Has Online delivery','Country']].agg({'Country': 'count','Has Table booking': 'sum','Has Online delivery': 'sum'}).rename(columns={'Country':'count'}).reset_index()
        capacidade_atendimento['indice'] = (capacidade_atendimento['Has Table booking'] * 0.5 + capacidade_atendimento['Has Online delivery'] * 0.5)
        fig = px.scatter(
            capacidade_atendimento, 
            x="count", 
            y="indice",
            text='Country',
            title='Capacidade de Atendimento: Número de Restaurantes vs Pontuação',
            labels={
                'count': 'Número de Resturantes',
                'indice': 'Pountuação'
            },
            height=600,
            template='plotly',
            hover_data={'Country': True}
        )


        fig.add_shape(
            type='line',
            x0=capacidade_atendimento['count'].min() * 19.44, x1=capacidade_atendimento['count'].max() / 2,
            y0=capacidade_atendimento['indice'].min(), y1=capacidade_atendimento['indice'].max() + 80,
            line=dict(dash='dash', color='Red'),
        )

        fig.add_shape(
            type='line',
            x0=capacidade_atendimento['count'].min() -70, x1=capacidade_atendimento['count'].max() + 100,
            y0=capacidade_atendimento['indice'].min() + 608.25 , y1=capacidade_atendimento['indice'].max() / 2,
            line=dict(dash='dash', color='Green'),
        )
        
        fig.add_annotation(
            x=750, y=950,
            text='Oportunidade de Expansão', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=950,
            text='Serviço de Qualidade', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=750, y=300,
            text='Necessidade de Transformação', 
            showarrow=False, 
            font=dict(size=20)
        )
        fig.add_annotation(
            x=2500, y=300,
            text='Necessidade de melhorias no Serviço', 
            showarrow=False, 
            arrowhead=1, 
            arrowsize=1, 
            arrowwidth=2, 
            font=dict(size=20)
        )

        fig.update_xaxes(showgrid=False)
        fig.update_yaxes(showgrid=False)
        fig.update_traces(textposition='bottom right')
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown(
             '''
    ### Como utilizar esse Gráfico? 
        -Alta Capacidade de Atendimento, Alta Avaliação:
            Serviço de Qualidade: Países onde os restaurantes oferecem tanto reservas de mesa quanto entregas online e possuem altas avaliações, indicando um serviço completo que atende bem às necessidades dos clientes.
            
        -Alta Capacidade de Atendimento, Baixa Avaliação:
            Necessidade de Melhorias no Serviço: Países onde os restaurantes oferecem reservas de mesa e entregas online, mas têm avaliações baixas, indicando que, embora o serviço esteja disponível, a execução precisa de melhorias.
            
        -Baixa Capacidade de Atendimento, Alta Avaliação:
            Oportunidade de Expansão: Países bem avaliados que não oferecem reservas de mesa ou entregas online, sugerindo uma oportunidade para expandir esses serviços e aumentar ainda mais a satisfação do cliente.
            
        -Baixa Capacidade de Atendimento, Baixa Avaliação:
            Necessidade de Transformação: Países onde os restaurantes não oferecem reservas de mesa nem entregas online e têm avaliações baixas, indicando um mercado que necessita de uma transformação significativa para se tornar competitivo.
     
'''
        )