# questions_test.py — basé sur les vraies données du projet GitHub

QA_PAIRS = [
    # Gouvernance
    {"question": "Qui est le directeur de l'ENSAM ?", "mots_cles_attendus": ["Samir", "BELFKIH", "Directeur"]},
    {"question": "Quel est l'email du directeur ?", "mots_cles_attendus": ["directeur@ensam"]},
    {"question": "Qui est le directeur adjoint des affaires pédagogiques ?", "mots_cles_attendus": ["adjoint", "pédagogique"]},
    {"question": "Qui est le directeur adjoint chargé de la recherche ?", "mots_cles_attendus": ["adjoint", "recherche"]},
    {"question": "Qui est le secrétaire général ?", "mots_cles_attendus": ["secrétaire", "général"]},
    {"question": "Qui est l'assistante de direction ?", "mots_cles_attendus": ["assistante", "direction"]},
    {"question": "Qui est responsable du département génie mécanique ?", "mots_cles_attendus": ["mécanique", "responsable"]},
    {"question": "Qui est responsable du département génie électrique ?", "mots_cles_attendus": ["électrique", "responsable"]},
    {"question": "Qui est responsable du département génie énergétique ?", "mots_cles_attendus": ["énergétique", "responsable"]},
    {"question": "Qui est responsable du département mathématiques appliquées ?", "mots_cles_attendus": ["mathématiques", "responsable"]},
    {"question": "Qui est responsable du département économie et management ?", "mots_cles_attendus": ["économie", "management"]},
    {"question": "Qui est responsable du département langues et communication ?", "mots_cles_attendus": ["langues", "communication"]},
    {"question": "Qui est responsable du département ingénierie des technologies de la santé ?", "mots_cles_attendus": ["santé", "ingénierie"]},
    {"question": "Quel est l'email de Pr. Azrar ?", "mots_cles_attendus": ["azrar", "@ensam"]},
    {"question": "Quel est l'email de Pr. Ouadi ?", "mots_cles_attendus": ["ouadi", "@ensam"]},
    {"question": "Quel est l'email de Pr. Zazi ?", "mots_cles_attendus": ["zazi", "@ensam"]},
    {"question": "Quel est l'email de Pr. Lotfi ?", "mots_cles_attendus": ["lotfi", "@ensam"]},

    # Formations Ingénieur
    {"question": "Quelles sont les formations disponibles à l'ENSAM ?", "mots_cles_attendus": ["génie", "ingénieur", "formation"]},
    {"question": "Quels sont les cycles de formation ?", "mots_cles_attendus": ["cycle", "ingénieur", "master"]},
    {"question": "Quels sont les débouchés du génie mécanique ?", "mots_cles_attendus": ["mécanique", "débouchés"]},
    {"question": "Quels sont les débouchés du génie biomédical ?", "mots_cles_attendus": ["biomédical", "débouchés"]},
    {"question": "Quels sont les débouchés de l'aéronautique ?", "mots_cles_attendus": ["aéronautique", "débouchés"]},
    {"question": "Quels sont les débouchés du génie industriel ?", "mots_cles_attendus": ["industriel", "débouchés"]},
    {"question": "Quels sont les débouchés de l'énergie électrique ?", "mots_cles_attendus": ["énergie", "électrique"]},
    {"question": "Quels sont les débouchés du génie des matériaux ?", "mots_cles_attendus": ["matériaux", "débouchés"]},
    {"question": "Quels sont les débouchés de l'ingénierie des systèmes énergétiques ?", "mots_cles_attendus": ["énergétique", "systèmes"]},
    {"question": "Quels sont les débouchés de la data science et intelligence artificielle ?", "mots_cles_attendus": ["data", "intelligence", "artificielle"]},
    {"question": "Qui est le coordonnateur du génie mécanique ?", "mots_cles_attendus": ["coordonnateur", "mécanique"]},
    {"question": "Qui est le coordonnateur du génie biomédical ?", "mots_cles_attendus": ["coordonnateur", "biomédical"]},
    {"question": "Qui est le coordonnateur de l'aéronautique ?", "mots_cles_attendus": ["coordonnateur", "aéronautique"]},
    {"question": "Qui est le coordonnateur du génie industriel ?", "mots_cles_attendus": ["coordonnateur", "industriel"]},
    {"question": "Qui est le coordonnateur de la data science ?", "mots_cles_attendus": ["coordonnateur", "data"]},
    {"question": "Quels sont les objectifs de la formation génie mécanique ?", "mots_cles_attendus": ["objectifs", "mécanique"]},
    {"question": "Quels sont les objectifs de la formation aéronautique ?", "mots_cles_attendus": ["objectifs", "aéronautique"]},
    {"question": "Quels sont les objectifs de la formation énergie électrique ?", "mots_cles_attendus": ["objectifs", "énergie"]},

    # Master
    {"question": "Quels sont les masters disponibles à l'ENSAM ?", "mots_cles_attendus": ["master", "ENSAM"]},
    {"question": "C'est quoi le master en mécanique avancée ?", "mots_cles_attendus": ["mécanique", "avancée", "master"]},
    {"question": "C'est quoi le master management de l'innovation ?", "mots_cles_attendus": ["management", "innovation", "master"]},
    {"question": "Quels sont les débouchés du master mécanique avancée ?", "mots_cles_attendus": ["mécanique", "débouchés"]},
    {"question": "Quels sont les débouchés du master management de l'innovation ?", "mots_cles_attendus": ["management", "débouchés"]},
    {"question": "Qui est le coordonnateur du master mécanique avancée ?", "mots_cles_attendus": ["coordonnateur", "mécanique"]},
    {"question": "Qui est le coordonnateur du master management de l'innovation ?", "mots_cles_attendus": ["coordonnateur", "management"]},

    # Classes Préparatoires
    {"question": "C'est quoi les classes préparatoires à l'ENSAM ?", "mots_cles_attendus": ["préparatoires", "ENSAM"]},
    {"question": "Quels sont les objectifs des classes préparatoires ?", "mots_cles_attendus": ["objectifs", "préparatoires"]},
    {"question": "Qui est le coordonnateur des classes préparatoires ?", "mots_cles_attendus": ["coordonnateur", "préparatoires"]},

    # Départements
    {"question": "Quels sont les départements de l'ENSAM ?", "mots_cles_attendus": ["département", "ENSAM"]},
    {"question": "C'est quoi le département génie mécanique ?", "mots_cles_attendus": ["mécanique", "département"]},
    {"question": "C'est quoi le département génie électrique ?", "mots_cles_attendus": ["électrique", "département"]},
    {"question": "C'est quoi le département génie énergétique ?", "mots_cles_attendus": ["énergétique", "département"]},
    {"question": "C'est quoi le département mathématiques appliquées ?", "mots_cles_attendus": ["mathématiques", "département"]},
    {"question": "C'est quoi le département économie et management ?", "mots_cles_attendus": ["économie", "management"]},
    {"question": "C'est quoi le département langues et communication ?", "mots_cles_attendus": ["langues", "communication"]},
    {"question": "C'est quoi le département ingénierie des technologies de la santé ?", "mots_cles_attendus": ["santé", "technologies"]},

    # Événements
    {"question": "Quels sont les événements de l'ENSAM ?", "mots_cles_attendus": ["événement", "ENSAM"]},
    {"question": "C'est quoi la Moroccan Robotics Week ?", "mots_cles_attendus": ["robotics", "Maroc"]},
    {"question": "C'est quoi le club RobotiCore ?", "mots_cles_attendus": ["RobotiCore", "club"]},
    {"question": "C'est quoi Innov4Talent ?", "mots_cles_attendus": ["Innov4Talent"]},
    {"question": "C'est quoi la CISTEM 2024 ?", "mots_cles_attendus": ["CISTEM", "2024"]},
    {"question": "C'est quoi la conférence IEEE-ICCITX.0 ?", "mots_cles_attendus": ["IEEE", "ICCITX"]},
    {"question": "C'est quoi la journée doctoriales ?", "mots_cles_attendus": ["doctoriales", "journée"]},
    {"question": "C'est quoi la journée internationale des femmes à l'ENSAM ?", "mots_cles_attendus": ["femmes", "internationale"]},
    {"question": "C'est quoi la cérémonie de remise des diplômes 2023 ?", "mots_cles_attendus": ["diplômes", "cérémonie", "2023"]},
    {"question": "C'est quoi le symposium sur la biomasse ?", "mots_cles_attendus": ["biomasse", "symposium"]},
    {"question": "Y a-t-il une coopération entre le Maroc et la Hongrie ?", "mots_cles_attendus": ["Maroc", "Hongrie", "coopération"]},
    {"question": "C'est quoi la conférence sur Mathematica ?", "mots_cles_attendus": ["Mathematica", "Wolfram"]},
    {"question": "C'est quoi la rencontre stage entreprise PFE 2024 ?", "mots_cles_attendus": ["stage", "PFE", "entreprise"]},
    {"question": "C'est quoi la plateforme 3DEXPERIENCE ?", "mots_cles_attendus": ["3DEXPERIENCE", "plateforme"]},

    # Description école
    {"question": "C'est quoi l'ENSAM ?", "mots_cles_attendus": ["école", "ingénieur", "arts et métiers"]},
    {"question": "Quelle est l'université de rattachement de l'ENSAM ?", "mots_cles_attendus": ["Mohammed V", "Rabat"]},
    {"question": "Quelle est l'approche pédagogique de l'ENSAM ?", "mots_cles_attendus": ["compétences", "learning"]},
    {"question": "Quels sont les objectifs pédagogiques de l'ENSAM ?", "mots_cles_attendus": ["objectifs", "compétences", "insertion"]},
    {"question": "C'est quoi le learning by doing ?", "mots_cles_attendus": ["learning", "doing", "pratique"]},
]