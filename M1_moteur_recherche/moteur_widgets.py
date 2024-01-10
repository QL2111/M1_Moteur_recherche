import ipywidgets as widgets

def thematique_widget():
    Thematique = widgets.Text(
        value='',
        placeholder='physiology',
        description='Thématique :',
        disabled=False
    )
    return Thematique

def nbarticleReddit_widget():
    nbArticle_Reddit = widgets.IntText(
        value=10,
        description='Nombre de document Reddit :',
        disabled=False
    )
    return nbArticle_Reddit

def nbarticleArvix_widget():
    nbArticle_Arvix = widgets.IntText(
        value=10,
        description='Nombre de document nbArticle_Arvix :',
        disabled=False
    )
    return nbArticle_Arvix

def mot_clefs_widget():
    Mot_clefs = widgets.Text(
        value='',
        placeholder='nteractive storytelling narratives',
        description='Mot cléfs :',
        disabled=False
    )
    return Mot_clefs
