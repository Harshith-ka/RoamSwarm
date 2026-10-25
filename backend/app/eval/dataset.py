"""
Curated AI Evaluation Benchmark Dataset for RoamSwarm (50 Landmarks).
Includes diverse categories:
- Well-documented iconic monuments
- Ambiguous place names (names existing in multiple cities)
- Sparse / poorly documented locations (minimal OSM tags)
- Conflicting or multi-period historical landmarks
"""

from typing import List, Dict, Any

EVALUATION_DATASET: List[Dict[str, Any]] = [
    # ----------------- Chennai Pilot Core (Iconic & Documented) -----------------
    {
        "id": "eval-01",
        "name": "Kapaleeshwarar Temple",
        "city": "Chennai",
        "latitude": 13.0334,
        "longitude": 80.2699,
        "category": "worship_hindu",
        "difficulty": "standard",
        "ground_truth_inception": "7th century",
        "expected_tags": ["amenity", "religion", "historic"]
    },
    {
        "id": "eval-02",
        "name": "San Thome Basilica",
        "city": "Chennai",
        "latitude": 13.0336,
        "longitude": 80.2785,
        "category": "worship_christian",
        "difficulty": "standard",
        "ground_truth_inception": "1523",
        "expected_tags": ["historic", "tourism"]
    },
    {
        "id": "eval-03",
        "name": "Fort St. George",
        "city": "Chennai",
        "latitude": 13.0797,
        "longitude": 80.2875,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "1644",
        "expected_tags": ["historic", "tourism"]
    },
    {
        "id": "eval-04",
        "name": "Ripon Building",
        "city": "Chennai",
        "latitude": 13.0827,
        "longitude": 80.2755,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1913",
        "expected_tags": ["historic", "building"]
    },
    {
        "id": "eval-05",
        "name": "Chennai Central Railway Station",
        "city": "Chennai",
        "latitude": 13.0825,
        "longitude": 80.2757,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1873",
        "expected_tags": ["railway", "historic"]
    },
    {
        "id": "eval-06",
        "name": "Marina Beach Lighthouse",
        "city": "Chennai",
        "latitude": 13.0399,
        "longitude": 80.2804,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1977",
        "expected_tags": ["man_made", "tourism"]
    },
    {
        "id": "eval-07",
        "name": "Government Museum Chennai",
        "city": "Chennai",
        "latitude": 13.0700,
        "longitude": 80.2560,
        "category": "museum",
        "difficulty": "standard",
        "ground_truth_inception": "1851",
        "expected_tags": ["tourism", "historic"]
    },
    {
        "id": "eval-08",
        "name": "Valluvar Kottam",
        "city": "Chennai",
        "latitude": 13.0538,
        "longitude": 80.2425,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1976",
        "expected_tags": ["historic", "memorial"]
    },
    {
        "id": "eval-09",
        "name": "Parthasarathy Temple",
        "city": "Chennai",
        "latitude": 13.0536,
        "longitude": 80.2762,
        "category": "worship_hindu",
        "difficulty": "standard",
        "ground_truth_inception": "8th century",
        "expected_tags": ["amenity", "historic"]
    },
    {
        "id": "eval-10",
        "name": "Madras High Court",
        "city": "Chennai",
        "latitude": 13.0877,
        "longitude": 80.2878,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1892",
        "expected_tags": ["historic", "building"]
    },

    # ----------------- Ambiguous Place Names (Test Disambiguation) -----------------
    {
        "id": "eval-11",
        "name": "St. Thomas Mount",
        "city": "Chennai",
        "latitude": 13.0049,
        "longitude": 80.1925,
        "category": "historical",
        "difficulty": "ambiguous",
        "disambiguation_note": "Can refer to suburban hill, army cantonment, or railway station",
        "expected_tags": ["historic", "place_of_worship"]
    },
    {
        "id": "eval-12",
        "name": "Government Museum",
        "city": "Chennai",
        "latitude": 13.0700,
        "longitude": 80.2560,
        "category": "museum",
        "difficulty": "ambiguous",
        "disambiguation_note": "Common generic name found in dozens of Indian states",
        "expected_tags": ["tourism"]
    },
    {
        "id": "eval-13",
        "name": "Victoria Memorial Hall",
        "city": "Chennai",
        "latitude": 13.0705,
        "longitude": 80.2570,
        "category": "heritage",
        "difficulty": "ambiguous",
        "disambiguation_note": "Often confused with Victoria Memorial in Kolkata",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-14",
        "name": "Senate House",
        "city": "Chennai",
        "latitude": 13.0645,
        "longitude": 80.2835,
        "category": "heritage",
        "difficulty": "ambiguous",
        "disambiguation_note": "Refers to Madras University campus building vs London Senate House",
        "expected_tags": ["historic", "building"]
    },
    {
        "id": "eval-15",
        "name": "National Art Gallery",
        "city": "Chennai",
        "latitude": 13.0712,
        "longitude": 80.2562,
        "category": "museum",
        "difficulty": "ambiguous",
        "disambiguation_note": "Generic museum title needing localized geocoding resolution",
        "expected_tags": ["tourism"]
    },

    # ----------------- Sparse / Low Metadata Landmarks -----------------
    {
        "id": "eval-16",
        "name": "Madras War Cemetery",
        "city": "Chennai",
        "latitude": 13.0232,
        "longitude": 80.1873,
        "category": "monument",
        "difficulty": "sparse",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-17",
        "name": "Thiruvalluvar Statue Ennore",
        "city": "Chennai",
        "latitude": 13.2012,
        "longitude": 80.3211,
        "category": "monument",
        "difficulty": "sparse",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-18",
        "name": "Puzhal Heritage Sluice",
        "city": "Chennai",
        "latitude": 13.1554,
        "longitude": 80.1772,
        "category": "heritage",
        "difficulty": "sparse",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-19",
        "name": "Old Washermanpet Clock Tower",
        "city": "Chennai",
        "latitude": 13.1098,
        "longitude": 80.2815,
        "category": "heritage",
        "difficulty": "sparse",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-20",
        "name": "Royapuram Railway Platform 1",
        "city": "Chennai",
        "latitude": 13.1070,
        "longitude": 80.2970,
        "category": "heritage",
        "difficulty": "sparse",
        "expected_tags": ["historic"]
    },

    # ----------------- Conflicting / Multi-Era Landmarks -----------------
    {
        "id": "eval-21",
        "name": "Mahabalipuram Shore Temple",
        "city": "Tamil Nadu",
        "latitude": 12.6163,
        "longitude": 80.1983,
        "category": "heritage",
        "difficulty": "conflicting",
        "disambiguation_note": "Contested dating between Rajasimha Pallava vs earlier rock structures",
        "expected_tags": ["historic", "heritage"]
    },
    {
        "id": "eval-22",
        "name": "Arjuna's Penance",
        "city": "Tamil Nadu",
        "latitude": 12.6175,
        "longitude": 80.1925,
        "category": "heritage",
        "difficulty": "conflicting",
        "disambiguation_note": "Disputed interpretation: Arjuna's Penance vs Descent of the Ganges",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-23",
        "name": "Five Rathas",
        "city": "Tamil Nadu",
        "latitude": 12.6092,
        "longitude": 80.1883,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "7th century",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-24",
        "name": "Krishna's Butterball",
        "city": "Tamil Nadu",
        "latitude": 12.6191,
        "longitude": 80.1932,
        "category": "attraction",
        "difficulty": "standard",
        "expected_tags": ["tourism"]
    },
    {
        "id": "eval-25",
        "name": "Sadras Dutch Fort",
        "city": "Tamil Nadu",
        "latitude": 12.5186,
        "longitude": 80.1614,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "1648",
        "expected_tags": ["historic"]
    },

    # ----------------- Pan-India Major Heritage Landmarks -----------------
    {
        "id": "eval-26",
        "name": "Gateway of India",
        "city": "Mumbai",
        "latitude": 18.9220,
        "longitude": 72.8347,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1924",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-27",
        "name": "Chhatrapati Shivaji Maharaj Terminus",
        "city": "Mumbai",
        "latitude": 18.9398,
        "longitude": 72.8355,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1887",
        "expected_tags": ["historic", "heritage"]
    },
    {
        "id": "eval-28",
        "name": "Elephanta Caves",
        "city": "Mumbai",
        "latitude": 18.9633,
        "longitude": 72.9315,
        "category": "heritage",
        "difficulty": "standard",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-29",
        "name": "Qutb Minar",
        "city": "Delhi",
        "latitude": 28.5245,
        "longitude": 77.1855,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1199",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-30",
        "name": "Humayun's Tomb",
        "city": "Delhi",
        "latitude": 28.5933,
        "longitude": 77.2507,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1570",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-31",
        "name": "Red Fort",
        "city": "Delhi",
        "latitude": 28.6562,
        "longitude": 77.2410,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "1648",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-32",
        "name": "India Gate",
        "city": "Delhi",
        "latitude": 28.6129,
        "longitude": 77.2295,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1931",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-33",
        "name": "Victoria Memorial",
        "city": "Kolkata",
        "latitude": 22.5448,
        "longitude": 88.3426,
        "category": "monument",
        "difficulty": "ambiguous",
        "ground_truth_inception": "1921",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-34",
        "name": "Howrah Bridge",
        "city": "Kolkata",
        "latitude": 22.5851,
        "longitude": 88.3468,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1943",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-35",
        "name": "Charminar",
        "city": "Hyderabad",
        "latitude": 17.3616,
        "longitude": 78.4747,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1591",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-36",
        "name": "Golconda Fort",
        "city": "Hyderabad",
        "latitude": 17.3833,
        "longitude": 78.4011,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "1143",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-37",
        "name": "Mysore Palace",
        "city": "Mysuru",
        "latitude": 12.3052,
        "longitude": 76.6552,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1912",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-38",
        "name": "Brihadisvara Temple",
        "city": "Thanjavur",
        "latitude": 10.7828,
        "longitude": 79.1318,
        "category": "worship_hindu",
        "difficulty": "standard",
        "ground_truth_inception": "1010",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-39",
        "name": "Meenakshi Temple",
        "city": "Madurai",
        "latitude": 9.9195,
        "longitude": 78.1193,
        "category": "worship_hindu",
        "difficulty": "standard",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-40",
        "name": "Hampi Virupaksha Temple",
        "city": "Hampi",
        "latitude": 15.3353,
        "longitude": 76.4600,
        "category": "worship_hindu",
        "difficulty": "standard",
        "ground_truth_inception": "7th century",
        "expected_tags": ["historic"]
    },

    # ----------------- Global International Benchmarks -----------------
    {
        "id": "eval-41",
        "name": "Eiffel Tower",
        "city": "Paris",
        "latitude": 48.8584,
        "longitude": 2.2945,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1889",
        "expected_tags": ["historic", "tourism"]
    },
    {
        "id": "eval-42",
        "name": "Louvre Museum",
        "city": "Paris",
        "latitude": 48.8606,
        "longitude": 2.3376,
        "category": "museum",
        "difficulty": "standard",
        "expected_tags": ["tourism"]
    },
    {
        "id": "eval-43",
        "name": "Big Ben",
        "city": "London",
        "latitude": 51.5007,
        "longitude": -0.1246,
        "category": "monument",
        "difficulty": "ambiguous",
        "disambiguation_note": "Officially Elizabeth Tower; Big Ben is the great bell",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-44",
        "name": "Tower Bridge",
        "city": "London",
        "latitude": 51.5055,
        "longitude": -0.0754,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1894",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-45",
        "name": "Colosseum",
        "city": "Rome",
        "latitude": 41.8902,
        "longitude": 12.4922,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "80 AD",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-46",
        "name": "Pantheon Rome",
        "city": "Rome",
        "latitude": 41.8986,
        "longitude": 12.4769,
        "category": "historical",
        "difficulty": "standard",
        "ground_truth_inception": "126 AD",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-47",
        "name": "Senso-ji",
        "city": "Tokyo",
        "latitude": 35.7148,
        "longitude": 139.7967,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "645 AD",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-48",
        "name": "Tokyo Tower",
        "city": "Tokyo",
        "latitude": 35.6586,
        "longitude": 139.7454,
        "category": "monument",
        "difficulty": "standard",
        "ground_truth_inception": "1958",
        "expected_tags": ["tourism"]
    },
    {
        "id": "eval-49",
        "name": "Fushimi Inari-taisha",
        "city": "Kyoto",
        "latitude": 34.9671,
        "longitude": 135.7727,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "711 AD",
        "expected_tags": ["historic"]
    },
    {
        "id": "eval-50",
        "name": "Kinkaku-ji",
        "city": "Kyoto",
        "latitude": 35.0394,
        "longitude": 135.7292,
        "category": "heritage",
        "difficulty": "standard",
        "ground_truth_inception": "1397",
        "expected_tags": ["historic"]
    }
]
