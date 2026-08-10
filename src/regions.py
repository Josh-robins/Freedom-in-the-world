"""Regional and country groupings used by the analysis.

The Freedom in the World dataset supplies **no regional classification**,
so every grouping here is an external, documented classification, mapped to
the dataset's own economy labels (the ``Economy`` column of the long
dataset). These groupings were explicitly approved for use in the project
(notebook 05, country analysis).

Sources:
- ``EAC_ECONOMIES``: East African Community member states (eac.int).
- ``SUPERPOWERS_P5_G7``: UN Security Council permanent members (P5) plus
  G7 members not already in the P5 (un.org / g7uk.org).
- ``AFRICA_UN_M49``: the 54 African member states of the United Nations,
  per the UN M49 geographic classification (unstats.un.org/unsd/methodology/m49).
- ``UN_M49_MAIN``: the five UN M49 main regions applied to all 197
  economies in the dataset (approved for notebook 06, regional analysis).
  Notes: Cyprus is classified to Western Asia per UN M49; Kosovo is not a
  UN member state and is assigned to Southern Europe per common M49-based
  usage; Puerto Rico and Hong Kong SAR are territories carried by the
  dataset and are classified with their M49 region.
- ``AFRICA_SUB_REGIONS``: the five UN M49 sub-regions of Africa.
"""

EAC_ECONOMIES = [
    "Uganda",
    "Kenya",
    "Tanzania",
    "Rwanda",
    "Burundi",
    "South Sudan",
    "Congo, Dem. Rep.",
    "Somalia",
]

SUPERPOWERS_P5_G7 = [
    "United States",
    "United Kingdom",
    "France",
    "Russian Federation",
    "China",
    "Germany",
    "Italy",
    "Japan",
    "Canada",
]

# User-selected East Africa subset for the notebook 08 map. This is the
# five-economy group chosen explicitly by the user (Uganda, Kenya,
# Tanzania, Rwanda, Burundi) - a subset of both EAC_ECONOMIES and the
# UN M49 Eastern Africa sub-region.
EAST_AFRICA_5 = [
    "Uganda",
    "Kenya",
    "Tanzania",
    "Rwanda",
    "Burundi",
]

AFRICA_UN_M49 = [
    "Algeria",
    "Angola",
    "Benin",
    "Botswana",
    "Burkina Faso",
    "Burundi",
    "Cabo Verde",
    "Cameroon",
    "Central African Republic",
    "Chad",
    "Comoros",
    "Congo, Dem. Rep.",
    "Congo, Rep.",
    "Cote d'Ivoire",
    "Djibouti",
    "Egypt, Arab Rep.",
    "Equatorial Guinea",
    "Eritrea",
    "Eswatini",
    "Ethiopia",
    "Gabon",
    "Gambia, The",
    "Ghana",
    "Guinea",
    "Guinea-Bissau",
    "Kenya",
    "Lesotho",
    "Liberia",
    "Libya",
    "Madagascar",
    "Malawi",
    "Mali",
    "Mauritania",
    "Mauritius",
    "Morocco",
    "Mozambique",
    "Namibia",
    "Niger",
    "Nigeria",
    "Rwanda",
    "Sao Tome and Principe",
    "Senegal",
    "Seychelles",
    "Sierra Leone",
    "Somalia",
    "South Africa",
    "South Sudan",
    "Sudan",
    "Togo",
    "Tunisia",
    "Uganda",
    "Tanzania",
    "Zambia",
    "Zimbabwe",
]

# --- UN M49 main regions (all 197 dataset economies) -------------------

UN_M49_MAIN = {
    "Africa": AFRICA_UN_M49,
    "Americas": [
        # Northern America
        "Canada",
        "United States",
        # Caribbean
        "Antigua and Barbuda",
        "Bahamas, The",
        "Barbados",
        "Cuba",
        "Dominica",
        "Dominican Republic",
        "Grenada",
        "Haiti",
        "Jamaica",
        "Puerto Rico",
        "St. Kitts and Nevis",
        "St. Lucia",
        "St. Vincent and the Grenadines",
        "Trinidad and Tobago",
        # Central America
        "Belize",
        "Costa Rica",
        "El Salvador",
        "Guatemala",
        "Honduras",
        "Mexico",
        "Nicaragua",
        "Panama",
        # South America
        "Argentina",
        "Bolivia",
        "Brazil",
        "Chile",
        "Colombia",
        "Ecuador",
        "Guyana",
        "Paraguay",
        "Peru",
        "Suriname",
        "Uruguay",
        "Venezuela, RB",
    ],
    "Asia": [
        # Central Asia
        "Kazakhstan",
        "Kyrgyz Republic",
        "Tajikistan",
        "Turkmenistan",
        "Uzbekistan",
        # Eastern Asia
        "China",
        "Hong Kong SAR, China",
        "Japan",
        "Korea, Dem. People's Rep.",
        "Korea, Rep.",
        "Mongolia",
        "Taiwan, China",
        # South-Eastern Asia
        "Brunei Darussalam",
        "Cambodia",
        "Indonesia",
        "Lao PDR",
        "Malaysia",
        "Myanmar",
        "Philippines",
        "Singapore",
        "Thailand",
        "Timor-Leste",
        "Viet Nam",
        # Southern Asia
        "Afghanistan",
        "Bangladesh",
        "Bhutan",
        "India",
        "Iran, Islamic Rep.",
        "Maldives",
        "Nepal",
        "Pakistan",
        "Sri Lanka",
        # Western Asia
        "Armenia",
        "Azerbaijan",
        "Bahrain",
        "Cyprus",
        "Georgia",
        "Iraq",
        "Israel",
        "Jordan",
        "Kuwait",
        "Lebanon",
        "Oman",
        "Qatar",
        "Saudi Arabia",
        "Syrian Arab Republic",
        "Turkiye",
        "United Arab Emirates",
        "Yemen, Rep.",
    ],
    "Europe": [
        # Eastern Europe
        "Belarus",
        "Bulgaria",
        "Czechia",
        "Hungary",
        "Moldova",
        "Poland",
        "Romania",
        "Russian Federation",
        "Slovak Republic",
        "Ukraine",
        # Northern Europe
        "Denmark",
        "Estonia",
        "Finland",
        "Iceland",
        "Ireland",
        "Latvia",
        "Lithuania",
        "Norway",
        "Sweden",
        "United Kingdom",
        # Southern Europe (Kosovo is not a UN member; assigned here per
        # common M49-based usage)
        "Albania",
        "Andorra",
        "Bosnia and Herzegovina",
        "Croatia",
        "Greece",
        "Italy",
        "Kosovo",
        "Malta",
        "Montenegro",
        "North Macedonia",
        "Portugal",
        "San Marino",
        "Serbia",
        "Slovenia",
        "Spain",
        # Western Europe
        "Austria",
        "Belgium",
        "France",
        "Germany",
        "Liechtenstein",
        "Luxembourg",
        "Monaco",
        "Netherlands",
        "Switzerland",
    ],
    "Oceania": [
        # Australia and New Zealand
        "Australia",
        "New Zealand",
        # Melanesia
        "Fiji",
        "Papua New Guinea",
        "Solomon Islands",
        "Vanuatu",
        # Micronesia
        "Kiribati",
        "Marshall Islands",
        "Micronesia, Fed. Sts.",
        "Nauru",
        "Palau",
        # Polynesia
        "Samoa",
        "Tonga",
        "Tuvalu",
    ],
}

# --- UN M49 sub-regions of Africa --------------------------------------

AFRICA_SUB_REGIONS = {
    "Eastern Africa": [
        "Burundi",
        "Comoros",
        "Djibouti",
        "Eritrea",
        "Ethiopia",
        "Kenya",
        "Madagascar",
        "Malawi",
        "Mauritius",
        "Mozambique",
        "Rwanda",
        "Seychelles",
        "Somalia",
        "South Sudan",
        "Tanzania",
        "Uganda",
        "Zambia",
        "Zimbabwe",
    ],
    "Middle Africa": [
        "Angola",
        "Cameroon",
        "Central African Republic",
        "Chad",
        "Congo, Dem. Rep.",
        "Congo, Rep.",
        "Equatorial Guinea",
        "Gabon",
        "Sao Tome and Principe",
    ],
    "Northern Africa": [
        "Algeria",
        "Egypt, Arab Rep.",
        "Libya",
        "Morocco",
        "Sudan",
        "Tunisia",
    ],
    "Southern Africa": [
        "Botswana",
        "Eswatini",
        "Lesotho",
        "Namibia",
        "South Africa",
    ],
    "Western Africa": [
        "Benin",
        "Burkina Faso",
        "Cabo Verde",
        "Cote d'Ivoire",
        "Gambia, The",
        "Ghana",
        "Guinea",
        "Guinea-Bissau",
        "Liberia",
        "Mali",
        "Mauritania",
        "Niger",
        "Nigeria",
        "Senegal",
        "Sierra Leone",
        "Togo",
    ],
}


def get_region_lookup():
    """Map every economy label to its UN M49 main region.

    Returns a dict ``{economy: region}`` covering exactly the 197
    economies in the dataset.
    """
    mapping = {}
    for region, members in UN_M49_MAIN.items():
        for member in members:
            if member in mapping:
                raise ValueError(f"Economy {member!r} assigned to two regions.")
            mapping[member] = region
    return mapping


def get_africa_subregion_lookup():
    """Map every African economy label to its UN M49 sub-region."""
    mapping = {}
    for subregion, members in AFRICA_SUB_REGIONS.items():
        for member in members:
            if member in mapping:
                raise ValueError(f"Economy {member!r} assigned to two sub-regions.")
            mapping[member] = subregion
    return mapping
