import calendar

from dash import html, dcc, Dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash.dependencies import Input, Output
import plotly.graph_objects as go
import pandas as pd

# initialisation de l'application
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, dbc.icons.BOOTSTRAP])

# lecture des donnees
fl = pd.read_csv('claude_csv/projet.csv', parse_dates=['order_date'])

em = pd.read_csv('claude_csv/note_projet.csv')

sa = pd.read_csv('claude_csv/projects.csv', encoding='ISO-8859-1')

ep = pd.read_csv('claude_csv/employees.csv')

# agreger les donnees par mois et par projet
df = fl.groupby([pd.Grouper(key='order_date', freq='M'), 'poduct_name']).sum().reset_index()
# agreger et sommer les montants par projet
dp = fl.groupby('poduct_name')['Revenue_projet'].sum()
# trier les donnees points du datarame
em = em.sort_values('nombre_points', ascending=False)
# convertir les dates en objet datetime pour leur exploitation
ep['date_emploi'] = pd.to_datetime(ep['date_emploi'])
ep['date_demission'] = pd.to_datetime(ep['date_demission'])

# construction de composants
header_component = html.H1("Visualiser vos données")

# graphe1:evolution des revenus d'un projet par annee

cumulfig = go.FigureWidget()

for name, group in df.groupby("poduct_name"):
    cumulfig.add_scatter(
        x=group["order_date"].dt.strftime("%b"),
        y=group["Revenue_projet"],
        mode="lines",
        name=name
    )

cumulfig.update_layout(
    title="Revenus par produit",
    xaxis_title="Date",
    yaxis_title="Revenu (en XAF)",
    xaxis=dict(
        tickformat="%b"
    )
)

# graphe 2: performances des differents produits par annee

piefig = go.FigureWidget(
    px.pie(
        labels=dp.index,
        values=dp.values,
        names=dp.index
    )
)

piefig.update_layout(
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
)

# graphe 3: classement du personnels par nombres de points dans l'entreprise

em['nombre_points'] = em['nombre_points'].apply(lambda x: round(x, 2))

# declaration des classes bootstrap utilisees pour customizer le tableau
table_header_class = 'table-header'
table_data_class = 'table-data'
table_row_odd_class = 'table-row-odd'
# configuration du tableau , la boucle permet ici de remplir le tableauen parcourant les 5 premieres lignes du dataframe
table_rows = []
for i in range(min(5, len(em))):
    row_class = table_row_odd_class if i % 2 == 0 else ''
    table_rows.append(html.Tr([
        html.Td(em.iloc[i]['first_name'], className=table_data_class),
        html.Td(em.iloc[i]['lastname'], className=table_data_class),
        html.Td(em.iloc[i]['nombre_points'], className=table_data_class), ]
        , className=row_class))

# graphe 4: suivi des activites ; table qui presente les activites et leurs statuts


sa['indice_rent'] = sa['indice_rent'].apply(lambda x: round(x, 2))

# declaration des classes bootstrap utilisees pour customizer le tableau
table_header_class = 'table-header'
table_data_class = 'table-data'
table_row_odd_class = 'table-row-odd'

# configuration du tableau , la boucle permet ici de remplir le tableau en parcourant les 5 premieres lignes du dataframe
table_rows1 = []
for i in range(len(sa)):
    row_class = table_row_odd_class if i % 2 == 0 else ''
    table_rows1.append(html.Tr([
        html.Td(sa.iloc[i]['product_name'], className=table_data_class),
        html.Td(sa.iloc[i]['indice_rent'], className=table_data_class),
        html.Td(sa.iloc[i]['statut'], className=table_data_class), ]
        , className=row_class))

# liste des projets pour le widget Dropdown

projectlist = [
    {"label": name, "value": name} for name in df["poduct_name"].unique()
]
# liste des annees pour le widget dropdown
default_year = 2022
yearlist = [
    {"label": year, "value": year} for year in df["order_date"].dt.year.unique()

]


# graphe 5 : presenter l'effectif du personnel par mois

# Definir la fonction pour calculer les effectifs du personnel present par mois

def count_employees(ep, year, month):
    periode = pd.Timestamp(year=year, month=month, day=calendar.monthrange(year, month)[1])    #periode designe la fin du mois
    present_employees = ep[
        (ep['date_emploi'] <= periode) & ((ep['date_demission'].isnull()) | (ep['date_demission'] >= periode))]

    return len(present_employees)


# creer une liste pour les mois et les annees

months = range(1, 13)
years = range(ep['date_emploi'].min().year, ep['date_emploi'].max().year + 1)


# callback pour mettre le graphe 1 a jour en fonction du projet selectionne et du l'annee selectionnee

@app.callback(
    Output('graph', 'figure'),
    [Input('list_dropdown', 'value'),
     Input('year_dropdown', 'value')])
def update_figure(projet, year):
    filter_df = df[df["poduct_name"] == projet]
    if year:
        filter_df = filter_df[filter_df["order_date"].dt.year == year]
    cumulfig.update_layout(title=f"Revenus pour le projet {projet}")

    cumulfig.data = []

    for name, group in filter_df.groupby("poduct_name"):
        cumulfig.add_scatter(
            x=group["order_date"].dt.strftime("%b"),
            y=group["Revenue_projet"],
            mode="lines",
            name=name
        )

    return cumulfig


# Callback pour mettre a jour le graphe 2 en fonction de l'annee selectionnee

@app.callback(
    Output('pie_graph', 'figure'),
    [Input('year2_dropdown', 'value')]
)
def update_pie(year2):
    if year2:
        filter_fl = fl[fl["order_date"].dt.year == year2]
    else:
        filter_fl = fl
    dp = filter_fl.groupby('poduct_name')['Revenue_projet'].sum()
    piefig = go.FigureWidget(
        px.pie(
            labels=dp.index,
            values=dp.values,
            names=dp.index
        )
    )
    piefig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    return piefig


# callback pour mettre a jour le graphe 5 en fonction de l'annee

# declaration des classes bootstrap utilisees pour customizer le tableau
table_header_class = 'table-header'
table_data_class = 'table-data'
table_row_odd_class = 'table-row-odd'

#ajout de la pagination ( utilise la biblio dcc)
pagination = dcc.Slider(

    id='table_pagination',
    min=0,
    max=2,
    step=1,
    value=0,
    marks={0: 'page 1 ', 1: 'page 2'}
)

@app.callback(
    Output('count_table', 'children'),
    [Input('year3_dropdown', 'value'), Input('table_pagination', 'value')]
)
def update_count_table(selected_year, page):
    # calculer les effectifs du personnel present pour chaque mois de l'annee
    employees_months = [count_employees(ep, selected_year, month) for month in months]
    # creer une liste de lignes pour le tableau
    table_rows2 = [html.Tr([
        html.Td(calendar.month_name[month], className=table_data_class),
        html.Td(employees_month, className=table_data_class),
    ], className=table_row_odd_class if month % 2 == 0 else '') for month, employees_month in zip(months, employees_months)]

    #pagination
    start = page * 6
    end = (page + 1) * 6
    return table_rows2[start:end]


# design du layout de l'application
app.layout = html.Div(
    [
        dbc.Row(
            [header_component

             ]
        ),
        dbc.Row(
            [dbc.Col(
                [
                    html.Label('selectionnez un projet'),
                    dcc.Dropdown(
                        id='list_dropdown',
                        options=projectlist,
                        value=df["poduct_name"].iloc[0]
                    ),
                    html.Label('selectionnez une annee'),
                    dcc.Dropdown(
                        id='year_dropdown',
                        options=yearlist,
                        value=default_year
                    ),
                    dcc.Graph(id='graph', figure=cumulfig)
                ]
            ), dbc.Col(
                [   html.H1('Performance des produits par une annee'),
                    html.Label('selectionnez une annee'),
                     dcc.Dropdown(
                         id='year2_dropdown',
                         options=yearlist,
                         value=default_year
                 ),
                 dcc.Graph(id='pie_graph', figure=piefig)
                 ]
            ), dbc.Col(
                [html.H1('Classement du Personnel par performance'),
                 html.Table([
                     html.Thead([
                         html.Tr([
                             html.Th('Nom', className=table_header_class),
                             html.Th('Prenom', className=table_header_class),
                             html.Th('Nombre de points', className=table_header_class)])
                     ]),
                     html.Tbody(table_rows)
                 ], className='table')]
            )]
        ),
        dbc.Row(
            [dbc.Col(
                [html.H1('suivi des activités'),
                 html.Table([
                     html.Thead([
                         html.Tr([
                             html.Th('Activités', className=table_header_class),
                             html.Th('indice de rentabilité', className=table_header_class),
                             html.Th('Statut', className=table_header_class)])
                     ]),
                     html.Tbody(table_rows1)
                 ], className='table')
                 ]
            ),
                dbc.Col(
                    [html.H1('Effectifs du personnel par mois'),

                     # ajouter la liste deroulante pour selectionner l'annee.
                     dcc.Dropdown(
                         id='year3_dropdown',
                         options=[{'label': str(year), 'value': year} for year in years],
                         value=years[-1]
                     ),

                     # ajout de la pagination
                     html.Div([
                        html.Label('Selectionnez la page:'),
                                             pagination,
                     ], style={'margin': '10px'}),


                     # creer le tableau pour afficher les effectifs du personnel par present par mois
                     html.Table([
                         html.Thead([
                             html.Tr([
                                 html.Th('Mois', className=table_header_class),
                                 html.Th('Effectifs du personnel present', className=table_header_class)
                             ])
                         ]),
                         html.Tbody(id='count_table', className='table-bordered'),
                     ], className='table table-striped')


                     ])
            ]),
    ])

# Demarrer l'application
if __name__ == '__main__':
    app.run_server(debug=True)
